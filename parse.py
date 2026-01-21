from bs4 import BeautifulSoup
from typing import List, Dict


def parse_realgm_stats(html: str) -> List[Dict[str, str]]:
    """
    Parse the main NBA stats table from RealGM.

    Input:
        html (str): Fully rendered HTML from fetch_playwright or fetch_http

    Output:
        List of dicts, one per player row, keyed by column header
    """
    soup = BeautifulSoup(html, "lxml")

    # Find all tables
    tables = soup.find_all("table")
    if not tables:
        raise ValueError("No tables found in HTML. Page structure may have changed.")

    expected_columns = {"Player", "Team"}
    target_table = None

    # Try to find the table with expected columns in any row (header or first row)
    for table in tables:
        # Check all rows for expected columns in headers or first row
        rows_to_check = []

        thead = table.find("thead")
        if thead:
            rows_to_check.extend(thead.find_all("tr"))
        tbody = table.find("tbody")
        if tbody:
            rows_to_check.extend(tbody.find_all("tr"))
        else:
            # If no tbody, check direct tr children of table
            rows_to_check.extend(table.find_all("tr"))

        for row in rows_to_check:
            cells = row.find_all(["th", "td"])
            headers = [cell.get_text(strip=True) for cell in cells]
            if expected_columns.intersection(headers):
                target_table = table
                break
        if target_table is not None:
            break

    if target_table is None:
        # Fallback to largest table by number of rows
        max_rows = -1
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) > max_rows:
                max_rows = len(rows)
                target_table = table
        print("Warning: Could not dynamically identify RealGM stats table by headers; using largest table. Table snippet:", str(target_table)[:200])

    table = target_table

    thead = table.find("thead")
    if thead:
        header_rows = thead.find_all("tr")
        if header_rows:
            # Use the first header row
            header_cells = header_rows[0].find_all("th")
        else:
            header_cells = []
    else:
        # Fallback: try first row in tbody as header
        tbody = table.find("tbody")
        if tbody:
            first_row = tbody.find("tr")
            if first_row:
                header_cells = first_row.find_all(["th", "td"])
                if not header_cells:
                    print("Warning: <thead> not found and first row in tbody has no header cells. Table snippet:", str(table)[:200])
                else:
                    print("Warning: <thead> not found, using first row in tbody as header. Table snippet:", str(table)[:200])
            else:
                header_cells = []
        else:
            header_cells = []

    if not header_cells:
        print("Warning: No header cells found in table. Table snippet:", str(table)[:200])
        raise ValueError("No headers found in RealGM stats table. Page structure may have changed.")

    headers = [cell.get_text(strip=True) for cell in header_cells]

    rows: List[Dict[str, str]] = []

    # Extract table body rows
    tbody = table.find("tbody")
    if tbody is None:
        # If no tbody, consider all tr except header row(s)
        data_rows = table.find_all("tr")
        # If header was taken from first row in tbody or thead, skip it in data rows
        if thead is None and data_rows:
            first_row_cells = data_rows[0].find_all(["th", "td"])
            first_row_texts = [cell.get_text(strip=True) for cell in first_row_cells]
            if first_row_texts == headers:
                data_rows = data_rows[1:]
    else:
        data_rows = tbody.find_all("tr")
        # If header was taken from first row in tbody, skip it in data rows
        if thead is None and data_rows:
            first_row_cells = data_rows[0].find_all(["th", "td"])
            first_row_texts = [cell.get_text(strip=True) for cell in first_row_cells]
            if first_row_texts == headers:
                data_rows = data_rows[1:]

    for tr in data_rows:
        cells = tr.find_all("td")
        if len(cells) != len(headers):
            # skip malformed rows
            continue

        cell_texts = [td.get_text(strip=True) for td in cells]
        row = dict(zip(headers, cell_texts))
        rows.append(row)

    return rows


if __name__ == "__main__":
    # Simple test for parse_realgm_stats
    example_html = """
    <table>
        <thead>
            <tr><th>Player</th><th>FG%</th><th>3PA</th><th>Team</th></tr>
        </thead>
        <tbody>
            <tr><td>LeBron James</td><td>52.3</td><td>8</td><td>LAL</td></tr>
            <tr><td>Stephen Curry</td><td>48.1</td><td>10</td><td>GSW</td></tr>
        </tbody>
    </table>
    """
    parsed_rows = parse_realgm_stats(example_html)
    for row in parsed_rows:
        print(row)