/* ========= VARIANT 2 — BRUTALIST · Space Grotesk ========= */

const V2 = ({ mode }) => {
  const D = window.PROMETEY_DATA;
  const isMob = mode === "mobile";
  return (
    <div className={`v2 v2-${mode}`} data-mode={mode}>
      {/* ---- WHY ---- */}
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
                <span className="v2-tag">PROОF/{String(i + 1).padStart(2, "0")}</span>
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

      {/* ---- SERVICES ---- */}
      <section className="v2-section v2-services">
        <div className="v2-rule">
          <span>[ ПОСЛУГИ / 02 ]</span>
          <span>4 НАПРЯМКИ</span>
        </div>
        <h2 className="v2-h2">
          ПОСЛУГИ <span className="v2-orange">/SERVICES</span>
        </h2>

        <div className="v2-svc-grid">
          {D.services.map((s, i) => (
            <article
              className="v2-svc-card"
              key={i}
              style={{ backgroundImage: `url(${isMob ? s.bgMobile : s.bg})` }}
            >
              <div className="v2-svc-num">
                <span className="v2-svc-num-big">{s.n}</span>
                <span className="v2-svc-num-tot">/04</span>
              </div>
              <div className="v2-svc-overlay" />
              <div className="v2-svc-body">
                <h3 className="v2-svc-title">{s.title}</h3>
                <p className="v2-svc-desc">{s.desc}</p>
                <button className="v2-btn">
                  <span>ДЕТАЛЬНІШЕ</span>
                  <span className="v2-arrow">→</span>
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* ---- CLIENTS ---- */}
      <section className="v2-section v2-clients">
        <div className="v2-rule">
          <span>[ КЛІЄНТИ / 03 ]</span>
          <span>{D.clients.length} BRANDS</span>
        </div>
        <h2 className="v2-h2">
          НАШІ <span className="v2-orange">КЛІЄНТИ</span>
        </h2>

        <div className="v2-clients-rail">
          {D.clients.map((c, i) => (
            <div className="v2-client" key={i}>
              <div className="v2-client-ring">
                <div className="v2-client-inner">
                  <img src={c.img} alt={c.name} />
                </div>
              </div>
              <span className="v2-client-name">{c.name}</span>
            </div>
          ))}
        </div>

        <div className="v2-clients-cta">
          <button className="v2-btn v2-btn-lg">
            <span>ПЕРЕГЛЯНУТИ ПОРТФОЛІО</span>
            <span className="v2-arrow">→</span>
          </button>
        </div>
      </section>

      {/* ---- CTA ---- */}
      <section className="v2-section v2-cta">
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
  );
};

window.V2 = V2;
