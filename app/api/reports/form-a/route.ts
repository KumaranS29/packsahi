import { NextResponse } from 'next/server'

function escapePdf(value: string) { return value.replace(/[()\\]/g, (m) => `\\${m}`).replace(/\n/g, ' ') }

export async function GET(request: Request) {
  const url = new URL(request.url)
  const id = url.searchParams.get('scan_id') ?? 'PKS-2026-0842'
  const verdict = url.searchParams.get('verdict') ?? 'FAIL'
  if (verdict !== 'FAIL') return NextResponse.json({ error: 'Form A is only available for failed inspections.' }, { status: 400 })
  const lines = [
    'GOVERNMENT OF INDIA', 'DoCA | LEGAL METROLOGY DIVISION', '',
    'FORM A - LEGAL SEIZURE & COMPOUNDING NOTICE', '', `Notice ID: ${id}`, `Date: ${new Date().toISOString()}`, 'Inspector: Aarav Mehta', 'Location: Delhi Circle', '',
    'VIOLATIONS', 'Rule 6 declarations require corrective action.', 'Rule 7 font-size requirement requires corrective action.', '', 'COMPOUNDING PENALTY', 'First offense: Rs. 10,000', '', 'This document is court-admissible.', 'Digital evidence hash: SHA-256 pending signature', '', 'Inspector signature: ____________________', 'Store manager signature: ____________________',
  ]
  const stream = `BT /F1 11 Tf 54 760 Td ${lines.map((line, index) => `${index ? '0 -18 Td ' : ''}(${escapePdf(line)}) Tj`).join(' ')} ET`
  const objects = [`<< /Type /Catalog /Pages 2 0 R >>`, `<< /Type /Pages /Kids [3 0 R] /Count 1 >>`, `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>`, `<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>`, `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`]
  let pdf = '%PDF-1.4\n'; const offsets = [0]
  objects.forEach((object, index) => { offsets.push(pdf.length); pdf += `${index + 1} 0 obj\n${object}\nendobj\n` })
  const xref = pdf.length; pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n${offsets.slice(1).map((offset) => String(offset).padStart(10, '0') + ' 00000 n ').join('\n')}\ntrailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`
  return new NextResponse(pdf, { headers: { 'Content-Type': 'application/pdf', 'Content-Disposition': `attachment; filename="form-a-${id}.pdf"` } })
}
