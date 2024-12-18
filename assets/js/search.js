import * as pagefind from "/pagefind/pagefind.js";

export class MBPagefindUI {
  constructor(options) {
    const {
      searchInput,
      template,
      output,
      loadMoreButton,
      statusOut,
      pageSize,
      sortRadios,
      ...pf_options
    } = options;

    this.searchInput = document.querySelector(searchInput);
    this.output = document.querySelector(output);
    this.loadMoreButton = document.querySelector(loadMoreButton);
    this.statusOut = document.querySelector(statusOut);

    this.template = {
      ...template,
      element: document.querySelector(template.element).cloneNode(true),
    };

    if (sortRadios) {
      this.sortRadios = Array.from(document.querySelectorAll(sortRadios));
    }
    this.sort = {};

    this.pageSize = pageSize ?? 5;

    this.pf_options = pf_options;
  }

  async init() {
    this.searchInput.addEventListener("input", this);
    this.searchInput.addEventListener("change", this);
    this.loadMoreButton.addEventListener("click", this);
    for (const el of this.sortRadios) {
      el.addEventListener("change", this);
    }
    await pagefind.options(this.pf_options);
    this.setSortState();
    if (this.searchInput.value) {
      await this.search(this.searchInput.value, { immediate: true });
    }
  }

  handleEvent(event) {
    if (event.currentTarget === this.searchInput) {
      this.search(event.currentTarget.value);
    } else if (event.currentTarget === this.loadMoreButton) {
      this.loadMore();
    } else if (this.sortRadios.includes(event.currentTarget)) {
      this.setSortState();
      this.search(this.searchInput.value, { immediate: true });
    }
  }

  async search(term, options = {}) {
    const { immediate = false } = options;
    const debounceDelay = immediate ? 0 : 300;
    const search = await pagefind.debouncedSearch(
      term,
      { sort: this.sort },
      debounceDelay,
    );
    if (search !== null) {
      return this.process(search.results, term);
    }
  }

  async process(results, term) {
    this.remainingResults = results;
    this.showStatus(results.length, term);
    await this.loadMore(true);
  }

  async loadMore(clearFirst = false) {
    if (this.remainingResults == null) {
      return;
    }
    const page = this.remainingResults.slice(0, this.pageSize);
    this.remainingResults =
      this.remainingResults.length > this.pageSize
        ? this.remainingResults.slice(this.pageSize)
        : null;
    const data = await Promise.all(page.map((r) => r.data()));
    if (clearFirst) {
      // doing this here means there's less of a flash of empty data when the
      // search changes
      this.clearOutput();
    }
    data.forEach((d) => this.showResult(d));
    this.setLoadMoreButton();
  }

  setLoadMoreButton() {
    this.loadMoreButton.hidden = !(this.remainingResults?.length > 0);
  }

  showResult(resultData) {
    const el = this.template.element.content.cloneNode(true);
    const title = el.querySelector(this.template.title);
    const excerpt = el.querySelector(this.template.excerpt);
    title.href = resultData.url;
    title.textContent = resultData.meta.title;
    excerpt.innerHTML = resultData.excerpt;

    this.output.appendChild(el);
  }

  clearOutput() {
    this.output.textContent = "";
  }

  showStatus(numResults, term) {
    if (term !== "") {
      this.statusOut.textContent = `${numResults} results for ${term}`;
    } else {
      this.statusOut.textContent = "";
    }
  }

  setSortState() {
    let key = this.sortRadios.find((el) => el.checked)?.value;
    if (key) {
      let value = "desc";
      if (key.includes(":")) {
        [key, value] = key.split(":");
      }
      this.sort = {
        [key]: value,
      };
    } else {
      this.sort = {};
    }
  }
}
