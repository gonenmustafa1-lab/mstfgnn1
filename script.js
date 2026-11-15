const PLAYLIST_URL = "https://raw.githubusercontent.com/gonenmustafa1-lab/mstfgnn1/main/tr.m3u";
const channelsWanted = [
  ["ATV","Ulusal"],["Kanal D","Ulusal"],["Show TV","Ulusal"],["Star TV","Ulusal"],
  ["NOW TV","Ulusal"],["TRT 1","TRT"],["TRT 2","TRT"],["TRT Belgesel","TRT"],
  ["TV8","Ulusal"],["Beyaz TV","Ulusal"],["Habertürk","Haber"],["CNN Türk","Haber"],
  ["NTV","Haber"],["A Haber","Haber"],["24 TV","Haber"],["TGRT Haber","Haber"]
];
const video=document.getElementById("video"), grid=document.getElementById("channelGrid"), statusEl=document.getElementById("status");
let hls=null, activeFilter="Tümü", allChannels=[];
const norm=s=>(s||"").toLocaleLowerCase("tr-TR").replace(/ı/g,"i").replace(/İ/g,"i").replace(/[^a-z0-9]/g,"");
function parseM3U(txt){
  const lines=txt.split(/\r?\n/);let meta="",out=[];
  for(const line of lines){if(line.startsWith("#EXTINF"))meta=line;else if(line.trim()&&!line.startsWith("#")&&meta){const name=(meta.split(",").pop()||"").trim();out.push({name,url:line.trim()});meta="";}}
  return out;
}
function findMatch(name, entries){
  const n=norm(name);
  return entries.find(e=>{const x=norm(e.name);return x===n||x.includes(n)||n.includes(x);});
}
function render(){
  const q=norm(document.getElementById("search").value);
  grid.innerHTML="";
  const list=allChannels.filter(c=>(activeFilter==="Tümü"||c.category===activeFilter)&&(!q||norm(c.name).includes(q)));
  if(!list.length){grid.innerHTML='<p class="status">Bu kategoride eşleşen kanal bulunamadı.</p>';return;}
  list.forEach(c=>{
    const b=document.createElement("button");b.className="channel"+(c===selected?" selected":"");b.type="button";
    const initials=c.name.replace(" TV","").split(" ").slice(0,2).map(x=>x[0]).join("").toUpperCase();
    b.innerHTML=`<span class="logo">${initials}</span><span><b>${c.name}</b><small>${c.url?"Canlı yayını aç":"Resmî yayın sayfası"}</small></span>`;
    b.addEventListener("click",()=>play(c));grid.appendChild(b);
  });
}
let selected=null;
function play(c){
  selected=c;document.getElementById("currentTitle").textContent=c.name;document.getElementById("placeholder").classList.add("hidden");render();
  if(!c.url){statusEl.textContent="Bu kanal için listede yayın adresi yok. Resmî yayın sayfası açılıyor.";if(c.fallback)window.open(c.fallback,"_blank","noopener");return;}
  statusEl.textContent="Yayın yükleniyor…";
  if(hls){hls.destroy();hls=null;}video.pause();video.removeAttribute("src");video.load();
  if(video.canPlayType("application/vnd.apple.mpegurl")){video.src=c.url;video.play().then(()=>statusEl.textContent="Canlı yayın oynatılıyor.").catch(()=>statusEl.textContent="Yayın başlamadı. Oynat düğmesine basın veya başka kanal deneyin.");}
  else if(window.Hls&&Hls.isSupported()){hls=new Hls();hls.loadSource(c.url);hls.attachMedia(video);hls.on(Hls.Events.MANIFEST_PARSED,()=>video.play().then(()=>statusEl.textContent="Canlı yayın oynatılıyor.").catch(()=>statusEl.textContent="Oynat düğmesine basın."));hls.on(Hls.Events.ERROR,(_,data)=>{if(data.fatal)statusEl.textContent="Bu yayın şu anda açılamıyor. Başka bir kanal deneyin.";});}
  else statusEl.textContent="Bu tarayıcı HLS yayınını desteklemiyor.";
}
async function init(){
  const wanted=channelsWanted;
  try{
    const r=await fetch(PLAYLIST_URL,{cache:"no-store"});if(!r.ok)throw new Error("playlist");
    const entries=parseM3U(await r.text());
    allChannels=wanted.map(([name,category])=>{const match=findMatch(name,entries);return {name,category,url:match?.url||"",fallback:name==="NOW TV"?"https://www.nowtv.com.tr/canli-yayin":""};});
    statusEl.textContent="Kanal listesi yüklendi. İzlemek için bir kanal seçin.";
  }catch(e){
    allChannels=wanted.map(([name,category])=>({name,category,url:"",fallback:name==="NOW TV"?"https://www.nowtv.com.tr/canli-yayin":""}));
    statusEl.textContent="Kanal listesi yüklenemedi. İnternet bağlantınızı kontrol edin.";
  }
  render();
}
document.getElementById("search").addEventListener("input",render);
document.getElementById("filters").addEventListener("click",e=>{const b=e.target.closest("button[data-filter]");if(!b)return;activeFilter=b.dataset.filter;document.querySelectorAll(".filter").forEach(x=>x.classList.toggle("active",x===b));render();});
document.getElementById("fullBtn").addEventListener("click",()=>{const box=document.getElementById("videoBox");if(box.requestFullscreen)box.requestFullscreen();else if(video.webkitEnterFullscreen)video.webkitEnterFullscreen();});
video.addEventListener("playing",()=>statusEl.textContent="Canlı yayın oynatılıyor.");
video.addEventListener("error",()=>{if(selected?.url)statusEl.textContent="Yayın oynatılamadı. Kaynak kapalı veya tarayıcı tarafından engelleniyor olabilir.";});
init();
