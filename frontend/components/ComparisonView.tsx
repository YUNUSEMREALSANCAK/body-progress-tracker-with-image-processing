'use client';

import { useState, ChangeEvent } from 'react';

import { API_URL } from '../utils/config';

export default function ComparisonView() {
  const [beforeImage, setBeforeImage] = useState<File | null>(null);
  const [afterImage, setAfterImage] = useState<File | null>(null);
  const [beforePreview, setBeforePreview] = useState<string | null>(null);
  const [afterPreview, setAfterPreview] = useState<string | null>(null);
  const [alignedImage, setAlignedImage] = useState<string | null>(null);

  // Overlay States
  const [beforeOverlay, setBeforeOverlay] = useState<string | null>(null);
  const [afterOverlay, setAfterOverlay] = useState<string | null>(null);
  const [showOverlay, setShowOverlay] = useState(true);

  const [loading, setLoading] = useState(false);
  const [opacity, setOpacity] = useState(50);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>, type: 'before' | 'after') => {
    const file = e.target.files?.[0];
    if (file) {
      if (type === 'before') {
        setBeforeImage(file);
        setBeforePreview(URL.createObjectURL(file));
        setBeforeOverlay(null);
      } else {
        setAfterImage(file);
        setAfterPreview(URL.createObjectURL(file));
        setAfterOverlay(null);
      }
      setAlignedImage(null);
    }
  };

  const handleAlign = async () => {
    if (!beforeImage || !afterImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('before_image', beforeImage);
    formData.append('after_image', afterImage);

    try {
      const response = await fetch(`${API_URL}/align`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        alert('Fotoğraflar işlenirken bir hata oluştu');
        throw new Error('Alignment failed');
      }

      const data = await response.json();

      // Clean Images (for slider)
      // data.before is the clean before image (actually we already have visual preview, 
      // but let's use what backend returned just in case it did some normalization? 
      // Actually backend returns decoded img1. Preview is blob. Blob is faster.
      // Let's stick to Preview for Before Base if possible? 
      // Wait, backend response might be slightly different dimensions if it resized?
      // No, align_images resizes img2 to match img1. img1 stays same.
      // But let's use backend response for consistent sizing potentially?
      // The user wants reliable comparison.
      // Let's use backend provided images to be safe.
      // Wait, ComparisonView uses 'beforePreview' for base. 'beforePreview' is local file blob.
      // Backend returns 'before' key which is img1.
      // Let's update beforePreview? No, keep it separate maybe?
      // Let's Render:
      // Base: data.before (Clean)
      // Overlay Photo: data.after (Clean, Aligned)
      // Overlay Lines 1: data.beforeAnalysis (Yellow)
      // Overlay Lines 2: data.afterAnalysis (Magenta)

      // We can reuse 'beforePreview' state for simplicity if we want, OR better:
      // use a new state 'processedBefore' to be sure we show exactly what alignment calculated against.

      // Update logic:
      // We will override 'beforePreview' with the clean image from backend to ensure 1:1 match with result?
      // Or just keep alignedImage logic.

      // Let's use a specific state for the Comparison View

      setAlignedImage(data.after); // Clean aligned after
      setBeforeOverlay(data.beforeAnalysis);
      setAfterOverlay(data.afterAnalysis);

      // Be careful: if we used local blob for 'Before', and backend returns 'Before', 
      // they should be same dimension.

    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-8 w-full max-w-4xl mx-auto p-4">
      <div className="grid grid-cols-2 gap-8 w-full">
        {/* Before Upload */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-lg text-gray-700">Before (Önce)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e, 'before')}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-violet-50 file:text-violet-700
              hover:file:bg-violet-100"
          />
          {beforePreview && (
            <img src={beforePreview} alt="Before" className="w-full h-64 object-contain bg-gray-100 rounded-lg" />
          )}
        </div>

        {/* After Upload */}
        <div className="flex flex-col gap-2">
          <label className="font-bold text-lg text-gray-700">After (Sonra)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e, 'after')}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-violet-50 file:text-violet-700
              hover:file:bg-violet-100"
          />
          {afterPreview && (
            <img src={afterPreview} alt="After" className="w-full h-64 object-contain bg-gray-100 rounded-lg" />
          )}
        </div>
      </div>

      <button
        onClick={handleAlign}
        disabled={!beforeImage || !afterImage || loading}
        className="px-8 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'İşleniyor...' : 'Fotoğrafları Hizala ve Karşılaştır'}
      </button>

      {/* Comparison Area */}
      {alignedImage && beforePreview && (
        <div className="w-full flex flex-col items-center gap-4 mt-8 border-t pt-8">
          <h2 className="text-2xl font-bold">Karşılaştırma</h2>

          {/* Controls */}
          <div className="flex gap-4 items-center mb-2">
            <label className="flex items-center gap-2 cursor-pointer bg-gray-100 px-4 py-2 rounded-lg border hover:bg-gray-200 transition">
              <input
                type="checkbox"
                checked={showOverlay}
                onChange={(e) => setShowOverlay(e.target.checked)}
                className="w-5 h-5 text-blue-600"
              />
              <span className="font-semibold text-gray-700">Analiz Çizgilerini Göster</span>
            </label>
            <div className="text-sm text-gray-500">
              <span className="text-yellow-600 font-bold">Sarı: Önce</span> | <span className="text-fuchsia-600 font-bold">Pembe: Sonra</span>
            </div>
          </div>

          <div className="relative w-full max-w-[500px] aspect-[3/4] border border-gray-300 rounded-lg overflow-hidden bg-gray-100">
            {/* 1. Base Image (Before Clean) */}
            <img
              src={beforePreview}
              alt="Base"
              className="absolute top-0 left-0 w-full h-full object-contain"
            />

            {/* 2. Aligned After Image (Clean) - Controlled by Slider */}
            <img
              src={alignedImage}
              alt="Overlay"
              className="absolute top-0 left-0 w-full h-full object-contain"
              style={{ opacity: opacity / 100 }}
            />

            {/* 3. Transparent Overlay Layers (Always visible if toggled) */}
            {showOverlay && beforeOverlay && (
              <img
                src={beforeOverlay}
                alt="Before Analysis"
                className="absolute top-0 left-0 w-full h-full object-contain pointer-events-none z-10"
              />
            )}
            {showOverlay && afterOverlay && (
              <img
                src={afterOverlay}
                alt="After Analysis"
                className="absolute top-0 left-0 w-full h-full object-contain pointer-events-none z-10"
              />
            )}
          </div>

          <div className="w-full max-w-[500px] flex flex-col gap-2">
            <label className="flex justify-between font-semibold text-gray-700">
              <span>Before (0%)</span>
              <span>After (100%)</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={opacity}
              onChange={(e) => setOpacity(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      )}
    </div>
  );
}
