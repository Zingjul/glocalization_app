//town_sync.js
document.addEventListener("DOMContentLoaded", function () {
  // Helper: find the "Unspecified" option (value '0' or '')
  function findUnspecified(select) {
    return (
      select.querySelector("option[value='0']") ||
      select.querySelector("option[value='']") ||
      null
    );
  }

  // Core logic: link a select + input pair
  function wirePair(select, input) {
    if (!select || !input) return;

    const unspecifiedOpt = findUnspecified(select);
    const unspecifiedValue = unspecifiedOpt ? unspecifiedOpt.value : null;
    if (unspecifiedValue === null) return;

    // Typing in input → switch dropdown to "Unspecified"
    input.addEventListener("input", function () {
      if (this.value.trim() !== "") {
        select.value = unspecifiedValue;
        if (unspecifiedOpt) unspecifiedOpt.style.display = "block";
      }
    });

    // Selecting a valid town → clear the text input
    select.addEventListener("change", function () {
      if (this.value !== unspecifiedValue) {
        input.value = "";
      }
    });
  }

  // 1️⃣ Preferred method: inside elements marked with [data-town-sync]
  document.querySelectorAll("[data-town-sync]").forEach(group => {
    const select =
      group.querySelector("select[name$='town']") ||
      group.querySelector("select[name$='post_town']") ||
      group.querySelector("select[id$='_town']") ||
      group.querySelector("select");

    const input =
      group.querySelector("input[name$='town_input']") ||
      group.querySelector("input[id$='_town_input']") ||
      group.querySelector("input[type='text']");

    wirePair(select, input);
  });

  // 2️⃣ Fallback: global pairs (in case no [data-town-sync] wrapper)
  [
    ["#id_town", "#id_town_input"],           // Person app
    ["#id_post_town", "#id_post_town_input"], // Posts app
  ].forEach(([selSel, inpSel]) => {
    const sel = document.querySelector(selSel);
    const inp = document.querySelector(inpSel);
    wirePair(sel, inp);
  });
});
