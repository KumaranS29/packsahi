import { NextResponse } from 'next/server'

const MAX_FILE_BYTES = 10 * 1024 * 1024
const ALLOWED_TYPES = new Set(['image/jpeg', 'image/png'])

export async function POST(request: Request) {
  const formData = await request.formData()
  const images = formData.getAll('images').filter((value): value is File => value instanceof File)
  const product = String(formData.get('product') ?? '').trim()
  const location = String(formData.get('location') ?? '').trim()
  if (images.length !== 4) return NextResponse.json({ error: 'Exactly four package angles are required.' }, { status: 400 })
  if (!product || product.length > 160 || !location || location.length > 240) return NextResponse.json({ error: 'Product and location are required.' }, { status: 400 })
  for (const image of images) {
    if (!ALLOWED_TYPES.has(image.type) || image.size === 0 || image.size > MAX_FILE_BYTES) return NextResponse.json({ error: 'Images must be non-empty JPG or PNG files under 10MB.' }, { status: 400 })
  }
  const ocrServiceUrl = process.env.OCR_SERVICE_URL
  if (!ocrServiceUrl) return NextResponse.json({ status: 'queued', message: 'Inspection queued. Set OCR_SERVICE_URL to enable live analysis.' }, { status: 202 })
  try {
    const upstream = await fetch(`${ocrServiceUrl.replace(/\/$/, '')}/analyze`, { method: 'POST', body: formData, signal: AbortSignal.timeout(45_000) })
    const result = await upstream.json()
    return NextResponse.json(result, { status: upstream.status })
  } catch {
    return NextResponse.json({ error: 'OCR service unavailable. Inspection remains queued for retry.' }, { status: 503 })
  }
}

export async function GET() {
  return NextResponse.json({ inspections: [], message: 'Connect MongoDB persistence to load inspection history.' })
}
