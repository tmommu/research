const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900},deviceScaleFactor:2});
const d='/tmp/claude-0/-home-user-research/a3ee1e49-b271-58df-97be-6a9699a16cde/scratchpad/';
await p.goto('file://'+d+'sagip_boat.html');await p.waitForTimeout(600);
const svgs=await p.$$('.scroll svg');
await svgs[0].screenshot({path:d+'fmt/fig_boat_side.png'});
await svgs[1].screenshot({path:d+'fmt/fig_patrol.png'});
await p.screenshot({path:'/home/user/research/sft_entry/SAGIP_Skimmer_Boat_Draft.png',fullPage:true});
await b.close();})();
