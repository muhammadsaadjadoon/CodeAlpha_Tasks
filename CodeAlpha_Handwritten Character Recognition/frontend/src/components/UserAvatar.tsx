import type {User} from '../types';
export function UserAvatar({user,className=''}:{user:User;className?:string}){const initials=user.full_name.split(/\s+/).filter(Boolean).map(x=>x[0]).slice(0,2).join('').toUpperCase();return <span className={`user-avatar ${className}`}><span>{initials}</span>{user.avatar_version>0&&<img src={`/api/profile/avatar?v=${user.avatar_version}`} alt=""/>}</span>}
