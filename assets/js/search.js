import * as pagefind from "/pagefind/pagefind.js";

export class MBPagefindUI {
  constructor(options) {
    const {
      searchInput,
      resultTemplate,
      output,
      loadMoreButton,
      statusOut,
      pageSize,
      sortRadios,
      filterSetContainer,
      filterSetTemplate,
      filterTemplate,
      ...pf_options
    } = options;

    // HTML Element inputs/outputs
    this.searchInput = document.querySelector(searchInput);
    this.output = document.querySelector(output);
    this.loadMoreButton = document.querySelector(loadMoreButton);
    this.statusOut = document.querySelector(statusOut);
    this.filterSetContainer = document.querySelector(filterSetContainer);
    if (sortRadios) {
      this.sortRadios = Array.from(document.querySelectorAll(sortRadios));
    }

    // Templates
    this.resultTemplate = {
      ...resultTemplate,
      element: document.querySelector(resultTemplate.element).cloneNode(true),
    };
    this.filterSetTemplate = {
      ...filterSetTemplate,
      element: document
        .querySelector(filterSetTemplate.element)
        .cloneNode(true),
    };
    this.filterTemplate = {
      ...filterTemplate,
      element: document.querySelector(filterTemplate.element).cloneNode(true),
    };

    // State
    this.filterAmountElements = {};
    this.filtersData = {};
    this.filtersState = {};

    // Options
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
    await this.loadFilters();
    if (this.searchInput.value) {
      await this.search(this.searchInput.value, { immediate: true });
    }
  }

  async loadFilters() {
    this.filtersData = await pagefind.filters();
    this.showFilters();
  }

  showFilters() {
    for (const filterSet of sortedKeys(this.filtersData)) {
      const filterSetTpl =
        this.filterSetTemplate.element.content.cloneNode(true);
      const title = filterSetTpl.querySelector(this.filterSetTemplate.title);
      const container = filterSetTpl.querySelector(
        this.filterSetTemplate.container,
      );

      title.textContent = kebabToTitleCase(filterSet);

      this.filterAmountElements[filterSet] = {};
      this.filtersState[filterSet] = { any: [] };

      for (const filter of sortedKeys(this.filtersData[filterSet])) {
        const filterTpl = this.filterTemplate.element.content.cloneNode(true);
        const input = filterTpl.querySelector(this.filterTemplate.input);
        const label = filterTpl.querySelector(this.filterTemplate.label);
        const name = filterTpl.querySelector(this.filterTemplate.name);
        const amount = filterTpl.querySelector(this.filterTemplate.amount);

        const id = `${filterSet}-${kebabCase(filter)}`;
        input.id = id;
        input.name = filter;
        label.htmlFor = id;
        name.textContent = filter;
        amount.textContent = `(${this.filtersData[filterSet][filter]})`;

        this.filterAmountElements[filterSet][filter] = amount;

        input.addEventListener("change", (event) => {
          if (event.currentTarget.checked) {
            this.filtersState[filterSet].any.push(filter);
          } else {
            this.filtersState[filterSet].any = this.filtersState[
              filterSet
            ].any.filter((f) => f !== filter);
          }
          this.search(this.searchInput.value, { immediate: true });
        });

        container.appendChild(filterTpl);
      }

      this.filterSetContainer.appendChild(filterSetTpl);
    }
  }

  updateFilterAmounts() {
    for (const filterSet in this.filtersData) {
      for (const filter in this.filtersData[filterSet]) {
        const amount = this.filterAmountElements[filterSet][filter];
        amount.textContent = `(${this.filtersData[filterSet][filter]})`;
      }
    }
  }

  handleEvent(event) {
    if (event.currentTarget === this.searchInput) {
      this.search(event.currentTarget.value);
    } else if (event.currentTarget === this.loadMoreButton) {
      this.loadMore();
    } else if (this.sortRadios.includes(event.currentTarget)) {
      this.search(this.searchInput.value, { immediate: true });
    }
  }

  async search(term, options = {}) {
    const { immediate = false } = options;
    const debounceDelay = immediate ? 0 : 300;
    const search = await pagefind.debouncedSearch(
      term,
      { sort: this.getSortState(), filters: this.filtersState },
      debounceDelay,
    );
    if (search !== null) {
      await this.process(search, term);
    }
  }

  async process(search, term) {
    const results = search.results;

    this.filtersData = search.totalFilters;
    this.updateFilterAmounts();

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
    const el = this.resultTemplate.element.content.cloneNode(true);
    const title = el.querySelector(this.resultTemplate.title);
    const excerpt = el.querySelector(this.resultTemplate.excerpt);
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

  getSortState() {
    let key = this.sortRadios.find((el) => el.checked)?.value;
    if (key) {
      let value = "desc";
      if (key.includes(":")) {
        [key, value] = key.split(":");
      }
      return {
        [key]: value,
      };
    } else {
      return {};
    }
  }
}

function kebabToTitleCase(str) {
  return str
    .replace(/\w-\w/g, (t) => `${t.charAt(0)} ${t.charAt(2).toUpperCase()}`)
    .replace(/^\w/, (t) => t.toUpperCase());
}

function kebabCase(str) {
  return str.toLowerCase().replace(" ", "-");
}

function sortedKeys(obj) {
  return Object.keys(obj).sort();
}
