import type {HistoryPage,ModelStatus,RecognitionResult,Theme,User} from './types';
async function request<T>(path:string,options:RequestInit={}):Promise<T>{
  const response=await fetch(path,{credentials:'include',...options,headers:{...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...(options.headers||{})}});
  if(!response.ok){let message='The request could not be completed.';try{const data=await response.json();message=data.detail||data.error||message}catch{}throw new Error(message)}
  return response.status===204?(undefined as T):response.json();
}
export const api={
  me:()=>request<User>('/api/auth/me'),
  register:(full_name:string,email:string,password:string)=>request<User>('/api/auth/register',{method:'POST',body:JSON.stringify({full_name,email,password})}),
  login:(email:string,password:string)=>request<User>('/api/auth/login',{method:'POST',body:JSON.stringify({email,password})}),
  logout:()=>request<void>('/api/auth/logout',{method:'POST'}),
  updateTheme:(theme:Theme)=>request<User>('/api/profile/theme',{method:'PATCH',body:JSON.stringify({theme})}),
  updateName:(full_name:string)=>request<User>('/api/profile/name',{method:'PATCH',body:JSON.stringify({full_name})}),
  updatePassword:(current_password:string,new_password:string)=>request<void>('/api/profile/password',{method:'PATCH',body:JSON.stringify({current_password,new_password})}),
  uploadAvatar:(file:File)=>{const f=new FormData();f.append('avatar',file);return request<User>('/api/profile/avatar',{method:'POST',body:f})},
  deleteAvatar:()=>request<User>('/api/profile/avatar',{method:'DELETE'}),
  recognize:(blob:Blob,filename:string,mode:string,sourceType:string)=>{const f=new FormData();f.append('image',blob,filename);f.append('mode',mode);f.append('source_type',sourceType);f.append('source_name',filename);return request<RecognitionResult>('/api/recognition/character',{method:'POST',body:f})},
  history:(limit=50,offset=0)=>request<HistoryPage>(`/api/recognition/history?limit=${limit}&offset=${offset}`),
  deleteHistory:(id:number)=>request<void>(`/api/recognition/history/${id}`,{method:'DELETE'}),
  clearHistory:()=>request<void>('/api/recognition/history',{method:'DELETE'}),
  modelStatus:()=>request<ModelStatus>('/api/model/status'),
  modelMetrics:()=>request<Record<string,unknown>>('/api/model/metrics'),
};
