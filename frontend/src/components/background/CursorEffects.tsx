import { useEffect } from "react";

function CursorEffects() {
  useEffect(() => {
    function handleMouseMove(event: MouseEvent) {
      document.documentElement.style.setProperty(
        "--cursor-x",
        `${event.clientX}px`,
      );

      document.documentElement.style.setProperty(
        "--cursor-y",
        `${event.clientY}px`,
      );
    }

    window.addEventListener("mousemove", handleMouseMove);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return null;
}

export default CursorEffects;
