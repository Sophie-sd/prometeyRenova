/* ========= VARIANT 3 — FUTURISTIC · Unbounded ========= */

const V3 = ({ mode }) => {
  const D = window.PROMETEY_DATA;
  const isMob = mode === "mobile";
  return (
    <div className={`v3 v3-${mode}`} data-mode={mode}>
      {/* glow bg */}
      <div className="v3-bg-glow v3-glow-a" aria-hidden="true" />
      <div className="v3-bg-glow v3-glow-b" aria-hidden="true" />
      <div className="v3-bg-grid" aria-hidden="true" />

      {/* ---- WHY ---- */}
      <section className="v3-section v3-why">
        <div className="v3-chip">— Чому ми</div>
        <h2 className="v3-h2">
          Чому варто обрати<br />
          <span className="v3-orange v3-glow-text">PrometeyLabs</span>
        </h2>
        <p className="v3-intro">{D.whyIntro}</p>

        <div className="v3-why-grid">
          {D.whyCards.map((c, i) => (
            <article className="v3-why-card" key={i}>
              <div className="v3-card-edge" aria-hidden="true" />
              <div className="v3-why-head">
                <div className="v3-why-icon-wrap">
                  <img src={c.icon} alt="" className="v3-why-icon" />
                </div>
                <span className="v3-why-num">0{i + 1}</span>
              </div>
              <h3 className="v3-why-title">
                <span className="v3-orange">{c.titleAccent}</span><br />
                {c.titleRest}
              </h3>
              <div className="v3-divider" />
              <p className="v3-why-sub">{c.subtitle}</p>
              <ul className="v3-why-list">
                {c.list.map(([k, v], j) => (
                  <li key={j}>
                    <span className="v3-bullet" aria-hidden="true" />
                    <span>
                      {k && <strong>{k} </strong>}
                      {v}
                    </span>
                  </li>
                ))}
              </ul>
              <p className="v3-why-note">{c.note}</p>
            </article>
          ))}
        </div>

        <div className="v3-why-foot">
          <p>{D.whyFooter}</p>
        </div>
      </section>

      {/* ---- SERVICES ---- */}
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

      {/* ---- CLIENTS ---- */}
      <section className="v3-section v3-clients">
        <div className="v3-chip">— Клієнти</div>
        <h2 className="v3-h2">
          Наші <span className="v3-orange v3-glow-text">клієнти</span>
        </h2>

        <div className="v3-clients-rail">
          {D.clients.map((c, i) => (
            <div className="v3-client" key={i}>
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

        <div className="v3-clients-cta">
          <button className="v3-btn v3-btn-lg">
            <span>Переглянути портфоліо</span>
            <span className="v3-arrow">↗</span>
          </button>
        </div>
      </section>

      {/* ---- CTA ---- */}
      <section className="v3-section v3-cta">
        <div className="v3-cta-card">
          <div className="v3-card-edge" aria-hidden="true" />
          <div className="v3-chip">— Старт проєкту</div>
          <h2 className="v3-h2 v3-cta-h2">
            Готові <span className="v3-orange v3-glow-text">почати?</span>
          </h2>
          <p className="v3-cta-text">{D.ctaText}</p>
          <div className="v3-cta-btns">
            <button className="v3-btn v3-btn-primary v3-btn-lg">
              <span>{D.ctaPrimary}</span>
              <span className="v3-arrow">↗</span>
            </button>
            <button className="v3-btn v3-btn-lg">
              <span>{D.ctaSecondary}</span>
              <span className="v3-arrow">↗</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

window.V3 = V3;
