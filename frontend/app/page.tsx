// Task T-201: Landing page for Phase II
// Route group: unauthenticated users see this, then redirected to signin/signup

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Evo-TODO</h1>
        <p className="text-xl text-gray-600 mb-8">
          Full-Stack Task Management with JWT Authentication
        </p>
        <div className="space-x-4">
          <a
            href="/signin"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Sign In
          </a>
          <a
            href="/signup"
            className="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Sign Up
          </a>
        </div>
      </div>
    </main>
  )
}
