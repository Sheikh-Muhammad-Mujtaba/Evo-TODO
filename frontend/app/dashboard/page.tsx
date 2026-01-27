'use client';

import ChatPage from './chat/page';

export default function Dashboard() {
  return (
    <div className="h-screen w-full">
      <ChatPage />  // T304/T305: Phase III direct Chat UI (no /todos redirect)
    </div>
  );
}
