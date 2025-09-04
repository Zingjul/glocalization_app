document.addEventListener("DOMContentLoaded", function () {
  function findUnspecified(select) {
    return (
      select.querySelector("option[value='0']") ||
      select.querySelector("option[value='']") ||
      null
    );
  }

  function wirePair(select, input) {
    if (!select || !input) return;

    const unspecifiedOpt = findUnspecified(select);
    const unspecifiedValue = unspecifiedOpt ? unspecifiedOpt.value : null;

    // If we can't determine an unspecified value, don't wire this pair.
    if (unspecifiedValue === null) return;

    // Typing into input => force dropdown to "Unspecified"
    input.addEventListener("input", function () {
      if (this.value.trim() !== "") {
        select.value = unspecifiedValue;
        if (unspecifiedOpt) unspecifiedOpt.style.display = "block";
      }
    });

    // Picking a real town => clear input
    select.addEventListener("change", function () {
      if (this.value !== unspecifiedValue) {
        input.value = "";
      }
    });
  }

  // 1) Preferred: wire pairs inside explicit containers
  document.querySelectorAll("[data-town-sync]").forEach(group => {
    // Try by name first (works for both Person and Post forms)
    const selectByName =
      group.querySelector("select[name$='town']") || // person: name="town"
      group.querySelector("select[name$='post_town']"); // posts: name="post_town"

    // Try by id/name/type fallbacks
    const select =
      selectByName ||
      group.querySelector("select[id$='_town']") ||
      group.querySelector("select");

    const inputByName =
      group.querySelector("input[name$='town_input']") ||       // person: town_input, posts: post_town_input
      group.querySelector("input[id$='_town_input']");

    const input =
      inputByName ||
      group.querySelector("input[type='text']");

    wirePair(select, input);
  });

  // 2) Safety net: if no container was used, wire well-known ids globally
  const globalPairs = [
    ["#id_town", "#id_town_input"],               // Person app
    ["#id_post_town", "#id_post_town_input"],     // Posts app
  ];
  globalPairs.forEach(([selSel, inpSel]) => {
    const sel = document.querySelector(selSel);
    const inp = document.querySelector(inpSel);
    wirePair(sel, inp);
  });
});

// document.addEventListener("DOMContentLoaded", function () {
//     // Find all "sync groups" (select + input pairs)
//     const syncGroups = document.querySelectorAll("[data-town-sync]");

//     syncGroups.forEach(group => {
//         const townSelect = group.querySelector("select");
//         const townInput  = group.querySelector("input[type='text']");

//         if (!townSelect || !townInput) return;

//         // Typing into input → force dropdown to "Unspecified Town"
//         townInput.addEventListener("input", function () {
//             if (this.value.trim() !== "") {
//                 townSelect.value = "0"; 
//                 const unspecified = townSelect.querySelector("option[value='0']");
//                 if (unspecified) {
//                     unspecified.style.display = "block";
//                 }
//             }
//         });

//         // Choosing a valid town → clear input
//         townSelect.addEventListener("change", function () {
//             if (this.value !== "0") {
//                 townInput.value = ""; 
//             }
//         });
//     });
// });


// document.addEventListener("DOMContentLoaded", function () {
//     const townSelect = document.getElementById("id_town");
//     const townInput  = document.getElementById("id_town_input");

//     if (townInput) {
//         // Typing into input automatically switches the dropdown to "Unspecified Town"
//         townInput.addEventListener("input", function () {
//             if (this.value.trim() !== "") {
//                 townSelect.value = "0"; 
//                 // Just to be extra safe, ensure the "Unspecified Town" option is visible when chosen
//                 const unspecified = townSelect.querySelector("option[value='0']");
//                 if (unspecified) {
//                     unspecified.style.display = "block";
//                 }
//             }
//         });
//     }

//     if (townSelect) {
//         // Selecting a valid town clears the custom input
//         townSelect.addEventListener("change", function () {
//             if (this.value !== "0") {
//                 townInput.value = ""; 
//             }
//         });
//     }
// });
