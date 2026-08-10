import {
  AudioLines,
  CheckCircle2,
  Headphones,
  Mic2,
  ShieldCheck,
  Sparkles,
  Volume2,
} from 'lucide-react';

const steps = [
  {
    icon: Mic2,
    title: 'Use a clear microphone position',
    text: 'Keep the microphone roughly 15–30 cm away and avoid touching the device while speaking.',
  },
  {
    icon: Volume2,
    title: 'Speak at a natural volume',
    text: 'Do not whisper or exaggerate. A normal sentence usually produces the most useful emotional signal.',
  },
  {
    icon: Headphones,
    title: 'Reduce background noise',
    text: 'Close noisy applications, move away from fans, and record in a quiet room whenever possible.',
  },
  {
    icon: AudioLines,
    title: 'Keep the sample focused',
    text: 'A continuous 3–15 second voice sample is ideal. Long pauses can reduce the quality of the estimate.',
  },
];

export function GuidePage() {
  return <div className="page-stack guide-page">
    <section className="guide-hero">
      <div>
        <span className="eyebrow"><Sparkles/>Recording guide</span>
        <h2>Get a cleaner signal in four simple steps.</h2>
        <p>These practical checks help INFLECT receive a clearer voice sample and produce a more useful emotional profile.</p>
      </div>
      <div className="guide-hero-note">
        <ShieldCheck/>
        <div><strong>Your recording stays private</strong><small>Original audio is removed after inference.</small></div>
      </div>
    </section>

    <section className="guide-grid">
      {steps.map(({ icon: Icon, title, text }, index) => <article className="panel guide-card" key={title}>
        <div className="guide-card-top"><span><Icon/></span><small>0{index + 1}</small></div>
        <h3>{title}</h3>
        <p>{text}</p>
      </article>)}
    </section>

    <section className="panel guide-checklist">
      <div>
        <span className="section-kicker">Before analysis</span>
        <h3>Quick quality checklist</h3>
      </div>
      <div className="guide-checks">
        <span><CheckCircle2/>Voice is easy to hear</span>
        <span><CheckCircle2/>No music or overlapping speakers</span>
        <span><CheckCircle2/>Sample contains natural speech</span>
        <span><CheckCircle2/>Recording is between 3 and 15 seconds</span>
      </div>
    </section>
  </div>;
}
