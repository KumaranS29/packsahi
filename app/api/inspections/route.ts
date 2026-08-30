import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const formData = await request.formData()
  const images = formData.getAll('images')
  if (images.length < 4) return NextResponse.json({ error: 'Four package angles are required.' }, { status: 400 })

  const ocrServiceUrl = process.env.OCR_SERVICE_URL
  if (!ocrServiceUrl) return NextResponse.json({ error: 'OCR service is not configured.' }, { status: 503 })

  const upstream = await fetch(`${ocrServiceUrl.replace(/\/$/, '')}/analyze`, { method: 'POST', body: formData })
  const result = await upstream.json()
  return NextResponse.json(result, { status: upstream.status })
}
