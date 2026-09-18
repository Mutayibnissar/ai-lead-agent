const API="/api";

const toast=document.querySelector("#toast");

function showToast(msg){
  if(!toast) return;
  toast.textContent=msg;
  toast.classList.add("show");
  clearTimeout(window.__t);
  window.__t=setTimeout(()=>toast.classList.remove("show"),2800);
}

async function api(path,options={}){
  const response=await fetch(API+path,{
    headers:{
      "Content-Type":"application/json",
      ...(options.headers||{})
    },
    ...options
  });

  if(!response.ok) throw new Error("API request failed");

  return response.status===204 ? {} : response.json();
}

async function checkBackend(){
  try{
    const health=await api("/health");
    if(health.ok){
      document.documentElement.dataset.api="online";
      console.info("KaamLab API connected",health);
    }
  }catch(error){
    document.documentElement.dataset.api="offline";
    console.info("KaamLab running in frontend/demo mode");
  }
}

document.querySelectorAll("[data-scroll]").forEach(button=>{
  button.addEventListener("click",()=>{
    document.querySelector(button.dataset.scroll)?.scrollIntoView({
      behavior:"smooth"
    });
  });
});

document.querySelectorAll("[data-demo]").forEach(button=>{
  button.addEventListener("click",async()=>{
    const type=button.dataset.demo;

    try{
      if(type==="brief"){
        const result=await api("/briefs",{
          method:"POST",
          body:JSON.stringify({
            title:"Sample local business digital campaign",
            business:"KaamLab Pilot Business",
            skills:"Content, Canva, social media",
            budget:"2500",
            description:"Create a practical campaign and measurable content plan for a local business."
          })
        });

        showToast("Sample brief created: "+result.title);
        return;
      }

      if(type==="talent"){
        const result=await api("/passport/demo-learner");

        showToast(
          "Talent Passport: "+
          (result.passport?.skills || 7)+
          " verified skills · "+
          (result.passport?.verifiedProjects || 4)+
          " projects"
        );

        return;
      }

      if(type==="hiring"){
        const result=await api("/applications");

        showToast(
          "Conversion workspace connected · "+
          (result.items?.length || 0)+
          " live applications"
        );

        return;
      }

    }catch(error){
      const fallback={
        brief:"Demo mode: start the GitHub Node backend with npm start to publish this brief.",
        talent:"Demo mode: start the GitHub Node backend to load the Talent Passport.",
        hiring:"Demo mode: start the GitHub Node backend to load applications."
      };

      showToast(fallback[type] || "KaamLab demo action");
    }
  });
});

checkBackend();