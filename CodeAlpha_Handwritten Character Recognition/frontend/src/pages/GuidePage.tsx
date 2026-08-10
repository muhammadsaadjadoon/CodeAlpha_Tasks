import {
  BookOpenCheck,
  CheckCircle2,
  Contrast,
  Crop,
  Image as ImageIcon,
  PenLine,
  ScanText,
  XCircle,
} from 'lucide-react';

const steps = [
  {
    icon: Crop,
    title: 'Frame one symbol',
    text: 'Crop tightly enough that one character clearly dominates the image.',
  },
  {
    icon: Contrast,
    title: 'Keep contrast clear',
    text: 'Dark writing on light paper is ideal; WriteLens corrects polarity automatically.',
  },
  {
    icon: PenLine,
    title: 'Use natural strokes',
    text: 'Avoid strokes that are extremely thin, clipped or touching the frame edges.',
  },
  {
    icon: ScanText,
    title: 'Pick the right mode',
    text: 'Use Digits mode when the input is definitely 0–9; otherwise use Characters or Auto.',
  },
];

export function GuidePage() {
  return (
    <div className="wl-page guide-page">
      <section className="page-hero">
        <div className="hero-copy">
          <span className="hero-index">04 · Recognition guide</span>
          <h1>Cleaner handwriting in. More useful prediction out.</h1>
          <p>
            The model can correct scale, polarity and centering, but a readable source
            image still gives the CNN a stronger signal.
          </p>
        </div>
      </section>

      <section className="guide-path">
        {steps.map(({ icon: Icon, title, text }, index) => (
          <article key={title}>
            <div className="guide-step-index">{String(index + 1).padStart(2, '0')}</div>
            <span className="guide-step-icon"><Icon /></span>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>

      <section className="guide-examples">
        <article className="guide-example good">
          <header>
            <span><CheckCircle2 /></span>
            <div><small>Recommended</small><strong>Give the model a clear target</strong></div>
          </header>
          <div className="guide-example-paper">
            <span>A</span>
          </div>
          <ul>
            <li>Single visible character</li>
            <li>Enough blank margin around the strokes</li>
            <li>Simple background with minimal shadow</li>
          </ul>
        </article>

        <article className="guide-example avoid">
          <header>
            <span><XCircle /></span>
            <div><small>Avoid</small><strong>Inputs that confuse segmentation</strong></div>
          </header>
          <div className="guide-example-paper noisy">
            <span>A7</span>
            <i />
            <i />
            <i />
          </div>
          <ul>
            <li>Multiple symbols in one image</li>
            <li>Character cut off at an edge</li>
            <li>Heavy texture, glare or extreme blur</li>
          </ul>
        </article>
      </section>

      <section className="guide-note">
        <BookOpenCheck />
        <div>
          <strong>Need a quick rule?</strong>
          <p>One character, centered, readable, with clean contrast.</p>
        </div>
        <ImageIcon />
      </section>
    </div>
  );
}
