/* ========= FINAL VARIANT — V3 base + V2 why + V2 centered CTA + animated partners ========= */

const VFinal = ({ mode }) => {
  const D = window.PROMETEY_DATA;
  const isMob = mode === "mobile";

  // Duplicate clients twice for seamless marquee loop
  const clientsLoop = [...D.clients, ...D.clients];

  return (
    <div className={`vf vf-${mode}`} data-mode={mode}>
      {/* ambient glows from V3 */}
      <div className="v3-bg-glow v3-glow-a" aria-hidden="true" />
      <div className="v3-bg-glow v3-glow-b" aria-hidden="true" />
      <div className="v3-bg-grid" aria-hidden="true" />

      {/* ---- WHY (V2 brutalist) ---- */}
      <div className={`v2 v2-${mode} vf-host`}>
        <section className="v2-section v2-why">
          <div className="v2-rule">
            <span>[ ЧОМУ МИ / 01 ]</span>
            <span>PROMETEYLABS — KYIV/UKRAINE</span>
          </div>
          <h2 className="v2-h2">
            ЧОМУ ВАРТО ОБРАТИ<br />
            <span className="v2-orange">PROMETEYLABS</span>
          </h2>
          <p className="v2-intro">{D.whyIntro}</p>

          <div className="v2-why-grid">
            {D.whyCards.map((c, i) => (
              <article className="v2-why-card" key={i}>
                <div className="v2-why-head">
                  <span className="v2-tag">PROOF/{String(i + 1).padStart(2, "0")}</span>
                  <img src={c.icon} alt="" className="v2-why-icon" />
                </div>
                <h3 className="v2-why-title">
                  <span className="v2-orange">{c.titleAccent}</span> {c.titleRest}
                </h3>
                <div className="v2-hr" />
                <p className="v2-why-sub">{c.subtitle}</p>
                <ul className="v2-why-list">
                  {c.list.map(([k, v], j) => (
                    <li key={j}>
                      <span className="v2-li-key">{k || "—"}</span>
                      <span className="v2-li-val">{v}</span>
                    </li>
                  ))}
                </ul>
                <p className="v2-why-note">{c.note}</p>
              </article>
            ))}
          </div>

          <div className="v2-why-foot">
            <span className="v2-tag v2-tag-solid">EXPERIENCE</span>
            <p>{D.whyFooter}</p>
          </div>
        </section>
      </div>

      {/* ---- SERVICES (V3 futuristic) ---- */}
      <div className={`v3 v3-${mode} vf-host vf-host-bare`}>
        <section className="v3-section v3-services">
          <div className="v3-chip">— Послуги</div>
          <h2 className="v3-h2">
            Послуги <span className="v3-orange v3-glow-text">PrometeyLabs</span>
          </h2>
          <div className="v3-svc-grid">
            {D.services.map((s, i) => (
              <article
                className="v3-svc-card"
                key={i}
                style={{ backgroundImage: `url(${isMob ? s.bgMobile : s.bg})` }}
              >
                <div className="v3-svc-edge" aria-hidden="true" />
                <div className="v3-svc-num">{s.n}</div>
                <div className="v3-svc-shade" />
                <div className="v3-svc-body">
                  <h3 className="v3-svc-title">{s.title}</h3>
                  <p className="v3-svc-desc">{s.desc}</p>
                  <button className="v3-btn">
                    <span>Детальніше</span>
                    <span className="v3-arrow">↗</span>
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>

      {/* ---- CLIENTS (V3 + animated marquee) ---- */}
      <div className={`v3 v3-${mode} vf-host vf-host-bare`}>
        <section className="v3-section v3-clients vf-clients-section">
          <div className="v3-chip">— Клієнти</div>
          <h2 className="v3-h2">
            Наші <span className="v3-orange v3-glow-text">клієнти</span>
          </h2>

          <div className="vf-clients-wrap">
            <div className="vf-clients-track">
              {clientsLoop.map((c, i) => (
                <div className="v3-client vf-client" key={i} aria-hidden={i >= D.clients.length}>
                  <div className="v3-client-halo" aria-hidden="true" />
                  <div className="v3-client-ring">
                    <div className="v3-client-inner">
                      <img src={c.img} alt={c.name} />
                    </div>
                  </div>
                  <span className="v3-client-name">{c.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="v3-clients-cta">
            <button className="v3-btn v3-btn-lg">
              <span>Переглянути портфоліо</span>
              <span className="v3-arrow">↗</span>
            </button>
          </div>
        </section>
      </div>

      {/* ---- CTA (V2 brutalist · centered) ---- */}
      <div className={`v2 v2-${mode} vf-host vf-cta-host`}>
        <section className="v2-section v2-cta vf-cta-center">
          <div className="v2-rule">
            <span>[ КОНТАКТ / 04 ]</span>
            <span>START PROJECT</span>
          </div>
          <h2 className="v2-h2 v2-cta-h2">
            ГОТОВІ <br />
            <span className="v2-orange">ПОЧАТИ?</span>
          </h2>
          <p className="v2-cta-text">{D.ctaText}</p>
          <div className="v2-cta-btns">
            <button className="v2-btn v2-btn-primary v2-btn-lg">
              <span>{D.ctaPrimary.toUpperCase()}</span>
              <span className="v2-arrow">→</span>
            </button>
            <button className="v2-btn v2-btn-lg">
              <span>{D.ctaSecondary.toUpperCase()}</span>
              <span className="v2-arrow">→</span>
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

window.VFinal = VFinal;
