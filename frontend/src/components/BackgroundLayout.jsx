import { useEffect, useState } from 'react';

function BackgroundLayout({ image, children }) {
  const [imageLoaded, setImageLoaded] = useState(false);

  useEffect(() => {
    // Preload image
    const img = new Image();
    img.src = image;
    img.onload = () => setImageLoaded(true);
  }, [image]);

  return (
    <div className="background-layout">
      <div 
        className="background-image"
        style={{
          backgroundImage: `url(${image})`,
          opacity: imageLoaded ? 1 : 0,
          transition: 'opacity 500ms ease-in-out'
        }}
      />
      <div className="background-overlay" />
      <div className="background-content">
        {children}
      </div>
      <style jsx>{`
        .background-layout {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          width: 100vw;
          height: 100vh;
          overflow: hidden;
        }

        .background-image {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          width: 100%;
          height: 100%;
          background-size: cover;
          background-position: center;
          background-repeat: no-repeat;
          z-index: -2;
        }

        .background-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(15, 12, 41, 0.75) 0%, rgba(48, 43, 99, 0.8) 50%, rgba(36, 36, 62, 0.75) 100%);
          z-index: -1;
        }

        .background-content {
          position: relative;
          width: 100%;
          height: 100%;
          overflow-y: auto;
        }
      `}</style>
    </div>
  );
}

export default BackgroundLayout;
