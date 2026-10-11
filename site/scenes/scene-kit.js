// Shared engine for every scene: the "smallest X that works" checklist, the
// floating progress pill, and acts that unlock as the reader plays.
//
// A scene page needs:
//   <ol id="mvp"> with one <li data-k="key"> per checklist item
//   <p id="mvpDone" hidden>   shown when every item is ticked
//   <a id="mvpPill">          the floating progress pill (phones)
//   <section class="act" id="..."> for each act
//
// Usage, from the scene's own script:
//   const kit = SceneKit.start({ pillLabel: "Locked box", locked: ["act2", "act3", "wrap"] });
//   kit.tick("out");      // tick a checklist item (safe to call twice)
//   kit.unlock("act2");   // open the next act
window.SceneKit = (function () {
  const $ = (id) => {
    const el = document.getElementById(id);
    if (!el) throw new Error(`Scene is missing #${id}`);
    return el;
  };

  function start({ pillLabel, locked = [] }) {
    const items = () => document.querySelectorAll("#mvp li[data-k]");
    const done = () => document.querySelectorAll("#mvp li[data-k].done");

    function renderPill(animate) {
      const pill = document.getElementById("mvpPill");
      if (!pill) return;
      const all = items().length, n = done().length;
      pill.textContent = `${pillLabel}: ${n}/${all}` + (n === all ? " ✓" : "");
      if (animate) { pill.classList.remove("pop"); void pill.offsetWidth; pill.classList.add("pop"); }
    }

    function tick(key) {
      const item = document.querySelector(`#mvp [data-k="${key}"]`);
      if (!item) throw new Error(`Checklist has no item "${key}"`);
      if (item.classList.contains("done")) return;
      item.classList.add("done", "pop");
      setTimeout(() => item.classList.remove("pop"), 600);
      renderPill(true);
      if (done().length === items().length) $("mvpDone").hidden = false;
    }

    // Locked acts are dimmed and fully unreachable: `inert` blocks clicks,
    // keyboard focus and screen readers until the act unlocks.
    function lock(id) { const el = $(id); el.classList.add("locked"); el.inert = true; }
    function unlock(id) { const el = $(id); el.classList.remove("locked"); el.inert = false; }

    locked.forEach(lock);
    renderPill(false);
    return { $, tick, unlock };
  }

  return { start };
})();
