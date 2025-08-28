// app/layout.tsx
import './globals.css';

export const metadata = { title: 'Job Tracker' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">
        <header className="border-b bg-white shadow-sm">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
            <h1 className="text-xl font-bold tracking-tight">Job Tracker</h1>
            <nav className="flex gap-4 text-sm text-gray-600">
              <a href="/" className="hover:text-gray-900">Jobs</a>
              <a href="#" className="hover:text-gray-900">About</a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
