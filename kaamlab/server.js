import http from "node:http";
import { randomUUID } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const PORT = process.env.PORT || 3000;
const ROOT = fileURLToPath(new URL(".", import.meta.url));
const briefs = [
  { id: randomUUID(), title:"Instagram content calendar", business:"Local apparel store", skills:"Content, Canva, social media", budget:"2500", status:"open", createdAt:new Date().toISOString() },
  { id: randomUUID(), title:"Improve product listings", business:"Local SME", skills:"E-commerce, copywriting", budget:"3000", status:"open", createdAt:new Date().toISOString() }
];
const applications = [];
const projects = [];
const passports = new Map();

const types={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".js":"text/javascript; charset=utf-8",".json":"application/json; charset=utf-8",".svg":"image/svg+xml",".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".ico":"image/x-icon"};

function json(res,status,data){
  res.writeHead(status,{"Content-Type":"application/json; charset=utf-8","Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"Content-Type","Access-Control-Allow-Methods":"GET,POST,OPTIONS"});
  res.end(JSON.stringify(data));
}
async function body(req){let raw="";for await(const chunk of req) raw+=chunk;return raw?JSON.parse(raw):{};}
function route(req){return new URL(req.url,`http://localhost:${PORT}`);}

async function serveStatic(req,res,url){
  if(req.method!=="GET") return false;
  let pathname=decodeURIComponent(url.pathname);
  if(pathname==="/") pathname="/index.html";
  if(pathname==="/dashboard") pathname="/mvp.html";
  if(pathname.startsWith("/api/")||pathname.includes("..")) return false;
  const file=join(ROOT,normalize(pathname.replace(/^\/+/, "")));
  try{
    const s=await stat(file);
    if(!s.isFile()) return false;
    const data=await readFile(file);
    res.writeHead(200,{"Content-Type":types[extname(file)]||"application/octet-stream","Cache-Control":"no-cache"});
    res.end(data); return true;
  }catch{return false;}
}

const server=http.createServer(async(req,res)=>{
  if(req.method==="OPTIONS") return json(res,204,{});
  const url=route(req);

  if(req.method==="GET"&&url.pathname==="/api/health") return json(res,200,{ok:true,service:"KaamLab API",time:new Date().toISOString()});
  if(req.method==="GET"&&url.pathname==="/api/briefs") return json(res,200,{items:briefs});
  if(req.method==="POST"&&url.pathname==="/api/briefs"){
    const b=await body(req); if(!b.title) return json(res,400,{error:"title is required"});
    const item={id:randomUUID(),title:b.title,business:b.business||"Demo business",skills:b.skills||"To be mapped",budget:b.budget||"Illustrative",description:b.description||"",status:"open",createdAt:new Date().toISOString()};
    briefs.unshift(item); return json(res,201,item);
  }
  if(req.method==="POST"&&url.pathname==="/api/applications"){
    const a=await body(req); if(!a.briefId||!a.learner) return json(res,400,{error:"briefId and learner are required"});
    const item={id:randomUUID(),...a,status:"submitted",createdAt:new Date().toISOString()}; applications.push(item); return json(res,201,item);
  }
  if(req.method==="GET"&&url.pathname==="/api/applications") return json(res,200,{items:applications});
  if(req.method==="POST"&&url.pathname==="/api/projects"){
    const p=await body(req); const item={id:randomUUID(),...p,status:p.status||"in_review",createdAt:new Date().toISOString()}; projects.push(item); return json(res,201,item);
  }
  if(req.method==="GET"&&url.pathname==="/api/projects") return json(res,200,{items:projects});
  if(req.method==="GET"&&url.pathname.startsWith("/api/passport/")){
    const learnerId=decodeURIComponent(url.pathname.split("/").pop());
    return json(res,200,{learnerId,passport:passports.get(learnerId)||{verifiedProjects:4,feedback:"4.8/5",skills:7,status:"Opportunity-ready",evidence:[]}});
  }
  if(req.method==="POST"&&url.pathname==="/api/passport"){
    const p=await body(req); if(!p.learnerId) return json(res,400,{error:"learnerId is required"}); passports.set(p.learnerId,p); return json(res,201,p);
  }
  if(req.method==="POST"&&url.pathname==="/api/ai"){
    const input=await body(req);
    return json(res,200,{mode:"demo",output:"KaamLab AI demo: structure the objective, deliverables, required micro-skills, constraints, deadline and success criteria.",received:input});
  }

  if(await serveStatic(req,res,url)) return;
  return json(res,404,{error:"Route not found"});
});
server.listen(PORT,()=>console.log(`KaamLab running on http://localhost:${PORT}`));
