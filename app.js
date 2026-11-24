// Proper BoltStack page logic.
//
// FORMSPREE SETUP: create a form at formspree.io, copy its ID (the part after /f/ in
// https://formspree.io/f/XXXXXXXX) and paste it below. Until then the form stays switched off.
var FORMSPREE_FORM_ID = "mgakrpob";

// The list itself lives in data/accomplishments.json. Only active items are shown.
fetch("data/accomplishments.json", { cache: "no-cache" })
  .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
  .then(function (data) {
    var items = data.accomplishments
      .filter(function (a) { return a.status === "active"; })
      .map(function (a) { return { n: a.number, vibe: a.vibe, title: a.title, proof: a.proof, capstone: a.capstone, series: a.series }; });
    // Show in number order, whatever order the file happens to be in.
    items.sort(function (x, y) { return x.n - y.n; });
    init(data.vibes, items);
  })
  .catch(function () {
    document.getElementById("groups").innerHTML =
      '<p class="empty">The list didn\'t load. Refresh the page to try again.</p>';
  });

function init(vibes, items) {
  var byKey = {};
  vibes.forEach(function (v) { byKey[v.key] = v; });

  // Black washers need an outline to show on the dark background.
  function swatch(el, color) {
    el.style.background = color;
    if (color === "#1c1c1c") el.style.boxShadow = "inset 0 0 0 1px #6b7178";
  }

  // --- Hero rod: one washer per vibe, capstones taller ---
  var rod = document.getElementById("rod");
  var start = document.createElement("div"); start.className = "bar start"; rod.appendChild(start);
  vibes.forEach(function (v) {
    for (var i = 0; i < 3; i++) {
      var w = document.createElement("div");
      w.className = "washer" + (i === 2 && v.key !== "roots" && v.key !== "degenerate" ? " cap" : "");
      swatch(w, v.color);
      rod.appendChild(w);
    }
  });
  var nut = document.createElement("div"); nut.className = "nut"; rod.appendChild(nut);
  var end = document.createElement("div"); end.className = "bar end"; rod.appendChild(end);

  // --- Filter chips ---
  var active = "all";
  var chips = document.getElementById("chips");
  function addChip(key, label, color) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.setAttribute("aria-pressed", key === active ? "true" : "false");
    if (color) { var d = document.createElement("span"); d.className = "dot"; swatch(d, color); b.appendChild(d); }
    b.appendChild(document.createTextNode(label));
    b.addEventListener("click", function () {
      active = key;
      Array.prototype.forEach.call(chips.children, function (c) { c.setAttribute("aria-pressed", "false"); });
      b.setAttribute("aria-pressed", "true");
      render();
    });
    chips.appendChild(b);
  }
  addChip("all", "All vibes", null);
  vibes.forEach(function (v) { addChip(v.key, v.name, v.color); });

  // --- List ---
  var openVibes = {};
  var search = document.getElementById("search");
  var groups = document.getElementById("groups");
  var count = document.getElementById("count");
  search.addEventListener("input", render);

  function render() {
    var q = search.value.trim().toLowerCase();
    groups.innerHTML = "";
    var shown = 0;
    vibes.forEach(function (v) {
      if (active !== "all" && active !== v.key) return;
      var list = items.filter(function (it) {
        return it.vibe === v.key && (!q || (it.title + " " + it.proof + " " + it.n).toLowerCase().indexOf(q) !== -1);
      });
      if (!list.length) return;
      shown += list.length;

      var wrap = document.createElement("details"); wrap.className = "vibe";
      wrap.dataset.vibe = v.key;
      // Closed by default; opened when filtering to one vibe or searching, or if the rider opened it.
      wrap.open = !!(q || active === v.key || openVibes[v.key]);
      wrap.addEventListener("toggle", function () { if (!q && active === "all") openVibes[v.key] = wrap.open; });
      var sum = document.createElement("summary");
      var icon = document.createElement("span"); icon.className = "washer-icon"; swatch(icon, v.color);
      var h = document.createElement("h3"); h.textContent = v.name;
      var meta = document.createElement("span"); meta.className = "meta";
      var total = items.filter(function (it) { return it.vibe === v.key; }).length;
      meta.textContent = q ? list.length + " of " + total + " match" : total + " propers";
      var chev = document.createElement("span"); chev.className = "chev"; chev.setAttribute("aria-hidden", "true"); chev.textContent = "\u203A";
      sum.appendChild(icon); sum.appendChild(h); sum.appendChild(meta); sum.appendChild(chev);
      wrap.appendChild(sum);
      var note = document.createElement("p"); note.className = "vibe-note"; note.textContent = v.note; wrap.appendChild(note);

      var ol = document.createElement("ol"); ol.className = "items";
      list.forEach(function (it) {
        var li = document.createElement("li");
        var num = document.createElement("span"); num.className = "num"; num.textContent = "#" + String(it.n).padStart(3, "0");
        var t = document.createElement("span"); t.className = "title"; t.textContent = it.title;
        if (it.capstone) {
          var cap = document.createElement("span"); cap.className = "cap-badge"; cap.textContent = "Capstone";
          cap.style.borderColor = v.color === "#1c1c1c" ? "#9aa0a6" : v.color;
          t.appendChild(cap);
        }
        var p = document.createElement("span"); p.className = "proof"; p.textContent = it.proof;
        li.appendChild(num); li.appendChild(t); li.appendChild(p);
        ol.appendChild(li);
      });
      wrap.appendChild(ol);
      groups.appendChild(wrap);
    });
    if (!shown) {
      var e = document.createElement("p"); e.className = "empty"; e.textContent = "Nothing matches that. Sounds like one to propose.";
      groups.appendChild(e);
    }
    count.textContent = shown === items.length ? "Showing all " + shown + "." : "Showing " + shown + " of " + items.length + ".";
  }
  render();

  // --- Proposal form ---
  var fold = document.getElementById("propose-fold");
  function openFoldFromHash() { if (location.hash === "#propose") fold.open = true; }
  window.addEventListener("hashchange", openFoldFromHash);
  openFoldFromHash();
  var form = document.getElementById("propose-form");
  var select = document.getElementById("vibe-select");
  var status = document.getElementById("form-status");
  var submit = form.querySelector("button.submit");

  var ph = document.createElement("option"); ph.value = ""; ph.textContent = "Pick one"; select.appendChild(ph);
  vibes.forEach(function (v) { var o = document.createElement("option"); o.value = v.name; o.textContent = v.name; select.appendChild(o); });
  var nv = document.createElement("option"); nv.value = "New vibe"; nv.textContent = "Doesn't fit any of these"; select.appendChild(nv);

  if (!FORMSPREE_FORM_ID) {
    document.getElementById("form-off").hidden = false;
    Array.prototype.forEach.call(form.elements, function (el) { el.disabled = true; });
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    status.className = "status"; status.textContent = "";
    var data = new FormData(form);
    if (!data.get("accomplishment") || !data.get("vibe") || !data.get("proof")) {
      status.className = "status err";
      status.textContent = "Fill in the accomplishment, the vibe, and how a stamper would check it.";
      return;
    }
    submit.disabled = true;
    status.textContent = "Sending...";
    fetch("https://formspree.io/f/" + FORMSPREE_FORM_ID, {
      method: "POST",
      body: data,
      headers: { "Accept": "application/json" }
    }).then(function (r) {
      if (r.ok) {
        form.reset();
        status.className = "status ok";
        status.textContent = "Got it, thanks. If it makes the list, you'll see it here.";
      } else {
        throw new Error();
      }
    }).catch(function () {
      status.className = "status err";
      status.textContent = "That didn't go through. Give it a minute and try again.";
    }).then(function () { submit.disabled = false; });
  });
}
