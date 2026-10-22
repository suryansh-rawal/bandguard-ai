import { Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Analyze from "./pages/Analyze";
import Report from "./pages/Report";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/analyze" element={<Analyze />} />
      <Route path="/report" element={<Report />} />
    </Routes>
  );
}