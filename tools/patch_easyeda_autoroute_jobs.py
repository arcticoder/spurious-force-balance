#!/usr/bin/env python3
"""Add the non-blocking autorouter job API to an installed EasyEDA Pro 3.2.x (docs/kb/easyeda_spark_notes.md).

The pro-api typings (api.js, already present) call PCB_Document.startAutoRouting / getAutoJobStatus /
cancelAutoJob / getAutoJobLog, but this app version has no handlers, so those calls hang until the
bridge times out. This script adds them:
  - pro-pcb/*/js/pcb.js: rpc services next to "autoRouting" (job record + progress taken from updateProgress)
  - pro-ui/*/js/ui.js:   Vg wrappers and the PCB_Document registry entries
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
MARK = 'startAutoRouting'


def patch(path, edits, revert):
    if revert:
        if os.path.exists(path + '.orig'):
            shutil.copyfile(path + '.orig', path)
            print('restored', path)
        return True
    s = open(path, encoding='utf8').read()
    if MARK in s:
        print('already patched', path)
        return True
    for anchor, new in edits:
        if s.count(anchor) != 1:
            print('anchor count', s.count(anchor), 'in', path, '- bundle changed, refusing:', anchor[:60])
            return False
        s = s.replace(anchor, new)
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
    ok = patch(pcb[0], [(PCB_ANCHOR, PCB_ANCHOR + PCB_ADD), (PCB_PROGRESS_ANCHOR, PCB_PROGRESS_ADD)], a.revert)
    ok = patch(ui[0], [(UI_ANCHOR, UI_ADD + UI_ANCHOR), (UI_REG_ANCHOR, UI_REG_ADD)], a.revert) and ok
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
