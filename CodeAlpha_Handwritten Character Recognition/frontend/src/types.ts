export type Theme='system'|'light'|'dark';
export type User={id:number;email:string;full_name:string;theme:Theme;avatar_version:number};
export type Score={label:string;probability:number};
export type RecognitionResult={id:number;primary_label:string;confidence:number;distribution:Score[];model_role:string;model_version:string;source_type:string;source_name:string;foreground_ratio:number;processed_preview:string|null;created_at:string};
export type HistoryPage={items:RecognitionResult[];total:number};
export type ModelStatus=Record<string,{name:string;ready:boolean;checkpoint:string;metrics_available:boolean}>;
