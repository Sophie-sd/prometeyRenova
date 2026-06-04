/* ========= VARIANT 1 — EDITORIAL · Manrope ========= */

const V1 = ({ mode }) => {
  const D = window.PROMETEY_DATA;
  const isMob = mode === "mobile";
  return (
    <div className={`v1 v1-${mode}`} data-mode={mode}>
      {/* ---- WHY CHOOSE ---- */}
      <section className="v1-section v1-why">
        <header className="v1-sec-head">
          <span className="v1-eyebrow">— 01 / Переваги</span>
          <h2 className="v1-h2">
            Чому варто обрати <span className="v1-orange">PrometeyLabs</span>
          </h2>
          <p className="v1-intro">{D.whyIntro}</p>
        </header>

        <div className="v1-why-grid">
          {D.whyCards.map((c, i) => (
            <article className="v1-why-card" key={i}>
              <div className="v1-why-top">
                <span className="v1-why-num">{String(i + 1).padStart(2, "0")}</span>
                <img src={c.icon} alt="" className="v1-why-icon" />
              </div>
              <h3 className="v1-why-title">
                <span className="v1-orange">{c.titleAccent}</span>{" "}
                <span className="v1-why-title-rest">{c.titleRest}</span>
              </h3>
              <p className="v1-why-sub">{c.subtitle}</p>
              <ul className="v1-why-list">
                {c.list.map(([k, v], j) => (
                  <li key={j}>
                    {k && <strong>{k} </strong>}
                    <span>{v}</span>
                  </li>
                ))}
              </ul>
              <p className="v1-why-note">{c.note}</p>
            </article>
          ))}
        </div>

        <div className="v1-why-foot">
          <span className="v1-foot-mark">★</span>
          <p>{D.whyFooter}</p>
        </div>
      </section>

      {/* ---- SERVICES ---- */}
      <section className="v1-section v1-services">
        <header className="v1-sec-head">
          <span className="v1-eyebrow">— 02 / Послуги</span>
          <h2 className="v1-h2">
            Послуги <span className="v1-orange">PrometeyLabs</span>
          </h2>
        </header>
        <div className="v1-svc-grid">
          {D.services.map((s, i) => (
            <article
              className="v1-svc-card"
              key={i}
              style={{ backgroundImage: `url(${isMob ? s.bgMobile : s.bg})` }}
            >
              <div className="v1-svc-num">{s.n}</div>
              <div className="v1-svc-shade" />
              <div className="v1-svc-body">
                <h3 className="v1-svc-title">{s.title}</h3>
                <p className="v1-svc-desc">{s.desc}</p>
                <button className="v1-btn-ghost">
                  Детальніше <span>↗</span>
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* ---- CLIENTS ---- */}
      <section className="v1-section v1-clients">
        <header className="v1-sec-head v1-sec-head-center">
          <span className="v1-eyebrow">— 03 / Клієнти</span>
          <h2 className="v1-h2">Наші клієнти</h2>
        </header>
        <div className="v1-clients-rail">
          {D.clients.map((c, i) => (
            <div className="v1-client" key={i}>
              <div className="v1-client-ring">
                <img src={c.img} alt={c.name} />
              </div>
              <span className="v1-client-name">{c.name}</span>
            </div>
          ))}
        </div>
        <div className="v1-clients-cta">
          <button className="v1-btn-ghost">
            Переглянути портфоліо <span>↗</span>
          </button>
        </div>
      </section>

      {/* ---- CTA ---- */}
      <section className="v1-section v1-cta">
        <div className="v1-cta-frame">
          <span className="v1-eyebrow">— 04 / Старт</span>
          <h2 className="v1-h2 v1-cta-h2">
            Готові <span className="v1-orange">почати?</span>
          </h2>
          <p className="v1-cta-text">{D.ctaText}</p>
          <div className="v1-cta-btns">
            <button className="v1-btn-primary">{D.ctaPrimary}</button>
            <button className="v1-btn-ghost">{D.ctaSecondary}</button>
          </div>
        </div>
      </section>
    </div>
  );
};

window.V1 = V1;
