#!/usr/bin/env python3
"""Add the non-blocking autorouter job API to an installed EasyEDA Pro 3.2.x (docs/kb/easyeda_spark_notes.md).

The pro-api typings (api.js, already present) call PCB_Document.startAutoRouting / getAutoJobStatus /
cancelAutoJob / getAutoJobLog, but this app version has no handlers, so those calls hang until the
bridge times out. This script adds them:
  - pro-pcb/*/js/pcb.js: rpc services next to "autoRouting" (job record + progress taken from updateProgress)
  - pro-pcb/*/js/pcb.js: also a `router` option ("pangolin" | "jrouter") that overrides the engine otherwise derived from `optimization`
  - pro-pcb/*/js/pcb.js: the 15-minute API timeout timer of an earlier job no longer kills a later job
  - pro-pcb/*/js/pcb.js: the API autoroute timeout is 60 minutes instead of 15
  - pro-api/*/api.js:    PCB_PrimitivePour.rebuildCopperById(id | ids) (rebuild copper without the MCP tool's persisted guard)
  - pro-ui/*/js/ui.js:   Vg wrappers and the PCB_Document registry entries
  - pro-api/*/api.js:    passes `router` through getAutoRoutingUserConfig; adds PCB_Drc.checkJson (the full DRC result
                         as a JSON string, because the bridge's normalizer replaces anything deeper than 5 levels with [MaxDepth])
Original files are kept as <file>.orig; `--revert` restores them. Restart EasyEDA afterwards (a restart kills a running
autoroute). Re-run after an EasyEDA update (the patch is idempotent; a changed bundle makes it refuse).

Usage: python3 -I tools/patch_easyeda_autoroute_jobs.py [--app DIR] [--revert]
"""
import argparse
import glob
import os
import shutil
import sys

PCB_ANCHOR = 'A.messageBus.rpcService("autoRouting",async i=>await x2.autoRouting(i,!1,!0)),'
PCB_ADD = (
    'A.messageBus.rpcService("startAutoRouting",async i=>{let j="ar"+Date.now(),J=globalThis.__arJob='
    '{jobId:j,state:"running",error:void 0,log:[{at:Date.now(),level:"info",message:"started"}]};'
    'globalThis.__arP={p:0,s:Date.now()};'
    'x2.autoRouting(i,!1,!0).then(r=>{J.log.push({at:Date.now(),level:r&&r.success?"info":"error",'
    'message:"finished "+JSON.stringify(r)});J.state==="running"&&(J.state=r&&r.success?"completed":"failed",'
    'r&&!r.success&&(J.error={code:"ROUTE_INCOMPLETE",message:"failed nets: "+(r.failedNets||[]).join(",")}))},'
    'e=>{J.log.push({at:Date.now(),level:"error",message:String(e&&e.message||e)});'
    'J.state==="running"&&(J.state="failed",J.error={code:"ROUTE_ERROR",message:String(e&&e.message||e)})});'
    'return{jobId:j}}),'
    'A.messageBus.rpcService("getAutoJobStatus",async id=>{let J=globalThis.__arJob;'
    'if(!J||J.jobId!==id)return;return{jobId:J.jobId,state:J.state,'
    'progress:Math.round(100*((globalThis.__arP||{}).p||0)),error:J.error,partial:J.state!=="running"}}),'
    'A.messageBus.rpcService("getAutoJobLog",async id=>{let J=globalThis.__arJob;'
    'return J&&J.jobId===id?J.log:[]}),'
    'A.messageBus.rpcService("cancelAutoJob",async id=>{let J=globalThis.__arJob;'
    'if(!J||J.jobId!==id||J.state!=="running")return!1;J.state="canceled";x2.routerInterrupt({manual:!0});return!0}),'
)
PCB_PROGRESS_ANCHOR = 'updateProgress(t,e,r=!0){if($().location.search.includes("pcbdebug"))return;'
PCB_PROGRESS_ADD = 'updateProgress(t,e,r=!0){globalThis.__arP={p:t,s:Date.now()};if($().location.search.includes("pcbdebug"))return;'

UI_ANCHOR = 'static async autoRouting(e){if(!vi())return{success:!1,totalNetsCount:0'
UI_ADD = (
    'static async startAutoRouting(e){let i=await ei(),{message:o}=await w.windowBridge.rpcCall("startAutoRouting",e,i.contentWindow,0);return o}'
    'static async getAutoJobStatus(e){let i=await ei(),{message:o}=await w.windowBridge.rpcCall("getAutoJobStatus",e,i.contentWindow);return o}'
    'static async getAutoJobLog(e){let i=await ei(),{message:o}=await w.windowBridge.rpcCall("getAutoJobLog",e,i.contentWindow);return o}'
    'static async cancelAutoJob(e){let i=await ei(),{message:o}=await w.windowBridge.rpcCall("cancelAutoJob",e,i.contentWindow);return o}'
)
UI_REG_ANCHOR = 'autoRouting:Vg.autoRouting}'
UI_REG_ADD = ('autoRouting:Vg.autoRouting,startAutoRouting:Vg.startAutoRouting,getAutoJobStatus:Vg.getAutoJobStatus,'
              'getAutoJobLog:Vg.getAutoJobLog,cancelAutoJob:Vg.cancelAutoJob}')
PCB_ROUTER_ANCHOR = 'let s=e?!1:((h=t==null?void 0:t.routingEffectPriority)!=null?h:this.config.routingEffectPriority)===0,'
PCB_ROUTER_ADD = ('let s=e?!1:t&&t.router==="jrouter"?!0:t&&t.router==="pangolin"?!1:'
                  '((h=t==null?void 0:t.routingEffectPriority)!=null?h:this.config.routingEffectPriority)===0,')
PCB_TIMER_ANCHOR = 'setTimeout(()=>{this.routingPromiseReject&&(this.routingPromiseReject(new Error("Auto routing timed out after 15 minutes"))'
PCB_TIMER_ADD = ('setTimeout(()=>{this.routingPromiseResolve===d&&this.routingPromiseReject&&'
                 '(this.routingPromiseReject(new Error("Auto routing timed out after 15 minutes"))')
DRC_ANCHOR = 'async check(t=!0,i=!1,n=!1){return await T.extensionApiMessageBus2.rpcCall("extensionApi.PCB_Drc.check",{strict:t,userInterface:i,includeVerboseError:n})}'
DRC_ADD = (DRC_ANCHOR + 'async checkJson(t=!0,i=!1,n=!0){let r=await this.check(t,i,n),st=[];'
           'return JSON.stringify(r,function(k,v){while(st.length&&st[st.length-1]!==this)st.pop();'
           'if(typeof v=="object"&&v!==null){if(st.includes(v))return"[Circular]";st.push(v)}'
           'else if(typeof v=="function")return"[Function]";return v})}')
POUR_ANCHOR = 'async getAll(t,i,n){let r={};return typeof t<"u"&&(r.net=t),typeof i<"u"&&(r.layer=i),typeof n<"u"&&(r.primitiveLock=n),(await T.extensionApiMessageBus2.rpcCall("extensionApi.PCB_PrimitivePour.getAll",r))'
POUR_ADD = ('async rebuildCopperById(t){let o=[];for(let i of(Array.isArray(t)?t:[t]))'
            'o.push(!!await T.extensionApiMessageBus2.rpcCall("extensionApi.PCB_PrimitivePour.rebuildCopperRegion",{ids:[i],isLast:!1}));return o}'
            + POUR_ANCHOR)
PCB_LIMIT_ANCHOR = 'let u=900*1e3;return new Promise((d,p)=>{'
PCB_LIMIT_ADD = 'let u=36e5;return new Promise((d,p)=>{'
API_ANCHOR = 'ignoreNets:(t==null?void 0:t.ignoreNets)||[],ignoreLayers:[]}'
API_ADD = 'ignoreNets:(t==null?void 0:t.ignoreNets)||[],ignoreLayers:[],router:t==null?void 0:t.router}'


def patch(path, edits, revert):
    if revert:
        if os.path.exists(path + '.orig'):
            shutil.copyfile(path + '.orig', path)
            print('restored', path)
        return True
    s = open(path, encoding='utf8').read()
    changed = False
    for anchor, new in edits:
        if new in s:
            continue
        if s.count(anchor) != 1:
            print('anchor count', s.count(anchor), 'in', path, '- bundle changed, refusing:', anchor[:60])
            return False
        s = s.replace(anchor, new)
        changed = True
    if not changed:
        print('already patched', path)
        return True
    if not os.path.exists(path + '.orig'):
        shutil.copyfile(path, path + '.orig')
    open(path, 'w', encoding='utf8').write(s)
    print('patched', path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--app', default='/opt/apps/easyeda-pro/resources/app')
    ap.add_argument('--revert', action='store_true')
    a = ap.parse_args()
    pcb = sorted(glob.glob(a.app + '/assets/pro-pcb/*/js/pcb.js'))
    ui = sorted(glob.glob(a.app + '/assets/pro-ui/*/js/ui.js'))
    if len(pcb) != 1 or len(ui) != 1:
        sys.exit('expected one pcb.js and one ui.js, found %d / %d' % (len(pcb), len(ui)))
    ok = patch(pcb[0], [(PCB_ANCHOR, PCB_ANCHOR + PCB_ADD), (PCB_PROGRESS_ANCHOR, PCB_PROGRESS_ADD),
                       (PCB_ROUTER_ANCHOR, PCB_ROUTER_ADD), (PCB_TIMER_ANCHOR, PCB_TIMER_ADD), (PCB_LIMIT_ANCHOR, PCB_LIMIT_ADD)], a.revert)
    ok = patch(ui[0], [(UI_ANCHOR, UI_ADD + UI_ANCHOR), (UI_REG_ANCHOR, UI_REG_ADD)], a.revert) and ok
    api = sorted(glob.glob(a.app + '/assets/pro-api/*/api.js'))
    if len(api) != 1:
        sys.exit('expected one api.js, found %d' % len(api))
    ok = patch(api[0], [(API_ANCHOR, API_ADD), (DRC_ANCHOR, DRC_ADD), (POUR_ANCHOR, POUR_ADD)], a.revert) and ok
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
