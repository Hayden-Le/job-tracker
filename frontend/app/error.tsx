'use client';
export default function Error({ error }: { error: Error }) {
  return (
    <div className="rounded border p-4">
      <h3 className="font-semibold">Something went wrong</h3>
      <p className="text-sm text-red-700">{error.message}</p>
    </div>
  );
}
