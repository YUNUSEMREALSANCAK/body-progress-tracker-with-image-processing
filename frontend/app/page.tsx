import ComparisonView from '../components/ComparisonView';
import AnalysisView from '../components/AnalysisView';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-white text-black">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex flex-col">
        <h1 className="text-4xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-violet-600">
          BodyProgress Tracker
        </h1>
        <p className="mb-12 text-center text-gray-500 max-w-2xl">
          Gelişim takibi için öncesi ve sonrası fotoğraflarınızı yükleyin.
          Yapay zeka sistemimiz fotoğrafları otomatik olarak hizalayacak ve karşılaştıracaktır.
        </p>

        <ComparisonView />

        <div className="w-full my-8 border-t border-gray-200"></div>

        <AnalysisView />
      </div>
    </main>
  );
}
