import { useLocation, Link, Navigate } from "react-router-dom";

export default function Report() {
  const { state } = useLocation();

  if (!state?.result) return <Navigate to="/analyze" replace />;

  return (
    <main className="mx-auto max-w-3xl p-6 flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Report</h1>
      <pre className="overflow-auto rounded bg-gray-100 p-4 text-sm">
        {JSON.stringify(state.result, null, 2)}
      </pre>
      <Link to="/analyze" className="underline">
        Analyze another
      </Link>
    </main>
  );
}