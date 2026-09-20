document$.subscribe(() => {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: document.body.getAttribute("data-md-color-scheme") === "slate" ? "dark" : "base",
    themeVariables: {
      primaryColor: "#f8edf5",
      primaryTextColor: "#51465b",
      primaryBorderColor: "#cfbad1",
      lineColor: "#98869f",
      secondaryColor: "#f4effb",
      tertiaryColor: "#fffafc"
    },
    flowchart: {
      curve: "basis",
      nodeSpacing: 28,
      rankSpacing: 46,
      useMaxWidth: true
    }
  });
  mermaid.run({ querySelector: ".mermaid" });
});

