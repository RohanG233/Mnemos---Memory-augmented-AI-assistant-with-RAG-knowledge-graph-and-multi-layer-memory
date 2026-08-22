import { useEffect, useRef } from "react";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

function NeuralBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvasElement = canvasRef.current;

    if (canvasElement === null) {
      return;
    }

    const contextElement = canvasElement.getContext("2d");

    if (contextElement === null) {
      return;
    }

    const canvas = canvasElement;
    const context = contextElement;

    let animationFrameId: number;

    const particles: Particle[] = [];

    const connectionDistance = 150;
    const cursorInfluenceDistance = 200;

    let mouseX = -1000;
    let mouseY = -1000;

    let smoothMouseX = -1000;
    let smoothMouseY = -1000;

    function resizeCanvas() {
      const pixelRatio = window.devicePixelRatio || 1;

      canvas.width = window.innerWidth * pixelRatio;
      canvas.height = window.innerHeight * pixelRatio;

      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;

      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    }

    function createParticles() {
      particles.length = 0;

      const particleCount = Math.min(
        180,
        Math.floor((window.innerWidth * window.innerHeight) / 12000),
      );

      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          vx: (Math.random() - 0.5) * 0.25,
          vy: (Math.random() - 0.5) * 0.25,
          radius: Math.random() * 1.5 + 0.5,
        });
      }
    }

    function handleMouseMove(event: MouseEvent) {
      mouseX = event.clientX;
      mouseY = event.clientY;
    }

    function handleMouseLeave() {
      mouseX = -1000;
      mouseY = -1000;
    }

    function draw() {
      context.clearRect(0, 0, window.innerWidth, window.innerHeight);

      /*
       * Smooth cursor movement.
       */

      smoothMouseX += (mouseX - smoothMouseX) * 0.08;

      smoothMouseY += (mouseY - smoothMouseY) * 0.08;

      /*
       * Move particles lightly.
       */

      for (const particle of particles) {
        particle.x += particle.vx;
        particle.y += particle.vy;

        /*
         * Keep particles inside the screen
         * by wrapping them around.
         */

        if (particle.x < 0) {
          particle.x = window.innerWidth;
        }

        if (particle.x > window.innerWidth) {
          particle.x = 0;
        }

        if (particle.y < 0) {
          particle.y = window.innerHeight;
        }

        if (particle.y > window.innerHeight) {
          particle.y = 0;
        }
      }

      /*
       * Draw connections.
       */

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const first = particles[i];
          const second = particles[j];

          const dx = first.x - second.x;
          const dy = first.y - second.y;

          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < connectionDistance) {
            const baseOpacity = (1 - distance / connectionDistance) * 0.4;

            /*
             * Connections become slightly brighter
             * near the cursor.
             */

            const firstCursorDistance = Math.sqrt(
              (first.x - smoothMouseX) ** 2 + (first.y - smoothMouseY) ** 2,
            );

            const secondCursorDistance = Math.sqrt(
              (second.x - smoothMouseX) ** 2 + (second.y - smoothMouseY) ** 2,
            );

            const cursorDistance = Math.min(
              firstCursorDistance,
              secondCursorDistance,
            );

            const cursorBoost =
              cursorDistance < cursorInfluenceDistance
                ? (1 - cursorDistance / cursorInfluenceDistance) * 0.25
                : 0;

            context.strokeStyle = `rgba(110, 100, 255, ${
              baseOpacity + cursorBoost
            })`;

            context.lineWidth = 0.6;

            context.beginPath();

            context.moveTo(first.x, first.y);
            context.lineTo(second.x, second.y);

            context.stroke();
          }
        }
      }

      /*
       * Draw particles.
       */

      for (const particle of particles) {
        const dx = particle.x - smoothMouseX;
        const dy = particle.y - smoothMouseY;

        const distance = Math.sqrt(dx * dx + dy * dy);

        /*
         * Particles near cursor glow slightly.
         */

        const cursorStrength =
          distance < cursorInfluenceDistance
            ? 1 - distance / cursorInfluenceDistance
            : 0;

        const radius = particle.radius + cursorStrength * 1.2;

        const opacity = 0.65 + cursorStrength * 0.35;

        context.beginPath();

        context.arc(particle.x, particle.y, radius, 0, Math.PI * 2);

        context.fillStyle = `rgba(120, 110, 255, ${opacity})`;

        context.fill();
      }

      /*
       * Soft cursor glow.
       */

      if (smoothMouseX > -500) {
        const gradient = context.createRadialGradient(
          smoothMouseX,
          smoothMouseY,
          0,
          smoothMouseX,
          smoothMouseY,
          cursorInfluenceDistance,
        );

        gradient.addColorStop(0, "rgba(110, 100, 255, 0.11)");

        gradient.addColorStop(0.45, "rgba(100, 232, 255, 0.07)");

        gradient.addColorStop(1, "rgba(110, 100, 255, 0)");

        context.fillStyle = gradient;

        context.beginPath();

        context.arc(
          smoothMouseX,
          smoothMouseY,
          cursorInfluenceDistance,
          0,
          Math.PI * 2,
        );

        context.fill();
      }

      animationFrameId = requestAnimationFrame(draw);
    }

    function handleResize() {
      resizeCanvas();
      createParticles();
    }

    resizeCanvas();
    createParticles();
    draw();

    window.addEventListener("mousemove", handleMouseMove);

    window.addEventListener("mouseleave", handleMouseLeave);

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);

      window.removeEventListener("mousemove", handleMouseMove);

      window.removeEventListener("mouseleave", handleMouseLeave);

      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas ref={canvasRef} className="neural-background" aria-hidden="true" />
  );
}

export default NeuralBackground;
