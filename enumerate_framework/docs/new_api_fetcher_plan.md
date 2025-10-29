# New API Fetcher Implementation Plan

Created: 2025-10-29

This plan captures the implementation path for four prioritized APIs that align with the "Enumerate All" philosophy. Each section lists required metadata, pagination mechanics, advanced question ideas, and engineering tasks to integrate the API into the framework.

## USGS Water Data OGC API
- **Goal:** Enumerate daily streamflow measurements for a defined Mississippi River segment starting 2024-01-01, ensuring completeness and threshold-based filtering.
- **Key Endpoints & Parameters:** Leverage the OGC `/observations` feature service with `limit` (<= 10000), `bbox`/`geoFilter`, and `startDate` query parameters. Follow `rel="next"` links until exhaustion.
- **Metadata to Capture:** `monitoringLocationIdentifier`, `monitoringLocationName`, `observedPropertyName`, `phenomenonTime`, `result`, `resultUom`, `lastUpdated`. Calculate daily rank by date if sorted.
- **Fetcher Tasks:**
  1. Prototype request builder supporting bounding boxes and temporal windows.
  2. Implement pagination iterator honoring `rel="next"` URLs and retry-on-429.
  3. Normalize results into deterministic ordering (primary sort by `phenomenonTime`, secondary by `monitoringLocationIdentifier`).
  4. Add schema validation to ensure units and observation type match expectations (e.g., discharge in cubic feet per second).
- **Advanced Question Draft:** “列出密西西比河选定河段自2024-01-01以来的全部日平均流量，返回测站ID、名称、日期、流量值、单位与更新时间，确认所有流量值 > 5000 cfs 的记录数。”
- **Testing Notes:** Mock short windows (3–5 days) for CI, provide recorded JSON fixture, and add integration toggle for live runs.

## Open Food Facts API
- **Goal:** Enumerate all gluten-free breakfast cereals sold in France, sorted by sugar content and enriched with nutrition metadata.
- **Key Endpoints & Parameters:** Use `/api/v2/search` with `page_size` (<= 1000), `page`, `countries_tags=france`, `labels_tags=gluten-free`, and `categories_tags=breakfast cereals`. Force deterministic sorting via `sort_by=nutriments.sugars_value`.
- **Metadata to Capture:** `code`, `product_name`, `brands_tags`, `nutriscore_grade`, `nutriments` (sugars, proteins, fat), `last_modified_t`, `quantity`, `url`.
- **Fetcher Tasks:**
  1. Build search helper that constructs filter strings and handles pagination until `count` exhausted.
  2. Normalize nutritional fields (grams per 100g) and convert timestamps.
  3. Implement sugar-based ranking field plus checksum to verify ordering.
  4. Add optional French-language name fallback when `product_name` missing.
- **Advanced Question Draft:** “列出法国市场的无麸质早餐麦片，提供条码、名称、Nutri-Score、每100g含糖量、最后更新时间，并验证按含糖量升序排列是否正确。”
- **Testing Notes:** Record minimal fixture with capped `page_size` for deterministic unit test; add smoke test that checks final page boundary.

## Cleveland Museum of Art Open Access API
- **Goal:** Enumerate all bronze sculptures in the collection with provenance and imagery, sorted by creation date.
- **Key Endpoints & Parameters:** Call `/artworks` with filters `q=type:sculpture AND technique:bronze`, `limit` (<= 100), `skip`, optional `has_image=1`.
- **Metadata to Capture:** `id`, `title`, `creators`, `creation_date`, `creation_date_earliest/latest`, `technique`, `culture`, `department`, `images.print.url`, `updated_at`.
- **Fetcher Tasks:**
  1. Implement query builder converting logical filters into CMA syntax.
  2. Handle pagination via `skip += limit` until `total` reached.
  3. Normalize date ranges into a sortable scalar (e.g., earliest year) for deterministic ordering.
  4. Store image URLs and provenance snippets (if available) for richer test prompts.
- **Advanced Question Draft:** “列举克利夫兰艺术博物馆藏的所有青铜雕塑，返回作品ID、标题、作者、创作年代、主要技法、图像链接，并按创作年代升序排列。”
- **Testing Notes:** Add fixture covering multi-page response; verify date normalization on partial/approximate year strings.

## National Archives Catalog API
- **Goal:** Enumerate photographic entries from Record Group 331 dated 1945–1950, ensuring cursor-based pagination integrity.
- **Key Endpoints & Parameters:** Use `/search` with `q=recordGroupNo:331 AND typeOfMaterial:Photographs AND coverageDates:[1945 TO 1950]`, `rows` (<= 1000), and `cursorMark` for deep paging.
- **Metadata to Capture:** `naId`, `title`, `description.scopeNote (scopeContent)`, `recordGroupNumber`, `coverageDates`, `productionDate`, `digitized` status, `objects.file.unit.publicCon`.
- **Fetcher Tasks:**
  1. Implement cursor loop storing `nextCursorMark` until no advancement.
  2. Flatten nested description fields and capture digital object URLs.
  3. Enforce deterministic ordering by `naId` when API sorting unspecified.
  4. Capture total hit count for verification and add assertion on sequential cursor usage.
- **Advanced Question Draft:** “枚举美国国家档案馆记录组331中1945-1950年的所有摄影条目，提供naId、标题、主题摘要、是否已数字化及数字对象链接，并检查是否检索到完整分页。”
- **Testing Notes:** Create unit test simulating two cursor pages; integration run should compare reported total vs. collected count.

## Shared Engineering Considerations
- Extend core pagination utilities to support both link-based and cursor-based patterns.
- Update documentation (`README_ENUMERATE_ALL.md`) after fetchers stabilize.
- Schedule rate-limit aware retries using exponential backoff where APIs signal throttling.
- Plan to register new test scenarios under `test_runners` with metadata-rich answers honoring ranking guidance.
