import { NextResponse } from 'next/server'

const records = [
 { scan_id:'PKS-2026-0842', product_name:'Sunfeast Dark Fantasy', brand_name:'ITC', verdict:'FAIL', location:'New Delhi', inspector_id:'INS-0042', timestamp:'2026-08-30T10:42:00Z' },
 { scan_id:'PKS-2026-0841', product_name:'Tata Salt Iodized', brand_name:'Tata', verdict:'PASS', location:'New Delhi', inspector_id:'INS-0042', timestamp:'2026-08-30T09:18:00Z' },
 { scan_id:'PKS-2026-0839', product_name:'Surf Excel Matic', brand_name:'HUL', verdict:'WARN', location:'New Delhi', inspector_id:'INS-0042', timestamp:'2026-08-29T16:36:00Z' },
]
export async function GET(request: Request) {
 const p = new URL(request.url).searchParams; const q=(p.get('q')??'').toLowerCase(); const verdict=p.get('verdict')??'ALL'; const page=Math.max(1,Number(p.get('page')??1)); const size=Math.min(100,Math.max(10,Number(p.get('size')??10)))
 const filtered=records.filter((r)=> (!q || Object.values(r).join(' ').toLowerCase().includes(q)) && (verdict==='ALL'||r.verdict===verdict)); const start=(page-1)*size
 return NextResponse.json({ data: filtered.slice(start,start+size), total:filtered.length, page, size, totalPages:Math.max(1,Math.ceil(filtered.length/size)) })
}
