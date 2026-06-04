/* Main composer — wires variants into a DesignCanvas with desktop + mobile side-by-side. */

const { DesignCanvas, DCSection, DCArtboard } = window;

// Heights are estimates that auto-grow with content; each artboard renders
// at its declared width and grows downward.
const VARIANTS = [
  {
    id: "vfinal",
    title: "★ Фінальний варіант",
    subtitle: "V3 (Unbounded) база + V2 (Space Grotesk) для 'Чому ми' + центрований V2 CTA + анімовані партнери",
    Comp: window.VFinal,
  },
  {
    id: "v1",
    title: "Варіант 1 · Editorial",
    subtitle: "Manrope · просторі сітки, тонкі помаранчеві акценти, дрібний номерний листинг",
    Comp: window.V1,
  },
  {
    id: "v2",
    title: "Варіант 2 · Brutalist",
    subtitle: "Space Grotesk + JetBrains Mono · щільна типографічна сітка, жорсткі помаранчеві бордюри",
    Comp: window.V2,
  },
  {
    id: "v3",
    title: "Варіант 3 · Futuristic",
    subtitle: "Unbounded · скляні картки з помаранчевим світінням, дисплейний шрифт, кінематографічний CTA",
    Comp: window.V3,
  },
];

const DESKTOP_W = 1280;
const MOBILE_W = 390;
const DESKTOP_H = 3400;
const MOBILE_H = 6000;

function App() {
  return (
    <DesignCanvas>
      {VARIANTS.map((v) => {
        const Comp = v.Comp;
        return (
          <DCSection key={v.id} id={v.id} title={v.title} subtitle={v.subtitle}>
            <DCArtboard
              id={`${v.id}-desktop`}
              label="Desktop · 1280"
              width={DESKTOP_W}
              height={DESKTOP_H}
            >
              <Comp mode="desktop" />
            </DCArtboard>
            <DCArtboard
              id={`${v.id}-mobile`}
              label="Mobile · 390"
              width={MOBILE_W}
              height={MOBILE_H}
            >
              <Comp mode="mobile" />
            </DCArtboard>
          </DCSection>
        );
      })}
    </DesignCanvas>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
