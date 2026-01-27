import { auth } from "@/lib/auth";
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest, { params }: { params: Promise<{ userId: string }> }) {
  try {
    console.log('[Chat API] Request received for userId:', await params);
    const { userId } = await params;
    const headers = await request.headers;
    const session = await auth.api.getSession({ headers });
    console.log('[Chat API] Session check:', !!session, session?.user.id === userId ? 'OK' : 'FAIL');
    if (!session || session.user.id !== userId) {
      console.log('[Chat API] Unauthorized');
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { message, conversation_id } = body;
    console.log('[Chat API] Message:', message, 'Conversation:', conversation_id);

    // Proxy to backend FastAPI chat endpoint (adjust URL as needed)
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    console.log('[Chat API] Backend URL:', backendUrl + '/api/chat');
    console.log('[Chat API] Auth header:', request.headers.get('Authorization') || 'none');
    console.log('[Chat API] Proxy body:', { message, conversation_id, user_id: userId });

    const backendRes = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({
        message,
        conversation_id,
        user_id: userId,
      }),
    });

    console.log('[Chat API] Backend response status:', backendRes.status, backendRes.statusText);

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      console.log('[Chat API] Backend error data:', errorData);
      return NextResponse.json({ error: errorData.error || 'Backend chat error' }, { status: backendRes.status });
    }

    const data = await backendRes.json();
    console.log('[Chat API] Backend success data:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('[Chat API] Full error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

