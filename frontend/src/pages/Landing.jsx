import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 p-6 text-center">
      <h1 className="text-4xl font-bold">BrandGuard AI</h1>
      <p className="max-w-md text-gray-600">
        Paste your text and check it against your brand guidelines.
      </p>
      <Link
        to="/analyze"
        className="rounded-lg bg-black px-6 py-3 text-white hover:opacity-80"
      >
        Get started
      </Link>
    </main>
  );
}