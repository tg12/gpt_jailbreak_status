import json

import pandas as pd
import requests
from fake_useragent import UserAgent
from tabulate import tabulate

ua = UserAgent()


headers = {
    "User-Agent": ua.random,
}


def get_json(url):
    result = None
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    if not response.ok:
        print("Server responded:", response.status_code)
    else:
        result = response.json()
        # pretty print
        print(json.dumps(result, indent=4, sort_keys=True))

    return result


def calculate_votes(data):
    """
    Calculate votes by subtracting downvotes from upvotes
    """
    for item in data:
        item["votes"] = item.pop("upvotes") - item.pop("downvotes")


def format_date(data):
    """
    Crop date
    """
    for item in data:
        item["created_at"] = item["created_at"][:10]


def set_output_cols(data, cols):
    """
    Filter data fields and set col order to cols
    """
    return [[item[key] for key in cols] for item in data]


def format_data(data, funcs):
    for func in funcs:
        func(data)


def scrape_jailbreak() -> pd.DataFrame:
    cols = ["votes", "name", "active", "created_at", "nsfw", "text"]
    data = get_json("https://www.jailbreakchat.com/api/getprompts")
    format_data(data, [calculate_votes, format_date])
    output = set_output_cols(data, cols)
    return pd.DataFrame(output, columns=cols)


def main():
    df = scrape_jailbreak()

    df = df.sort_values(by="votes", ascending=False)
    # print the unique values of the name column where they are active and
    # also where they aren't
    print(df[df["active"]]["name"].unique())
    print(df[df["active"] == False]["name"].unique())
    print("------------------")
    df.loc[df["active"] == False, df.columns != "name"] = "***PATCHED***"
    # drop votes, active, nsfw, created_at columns
    df = df.drop(columns=["votes", "active", "nsfw", "created_at"])
    # add a new column called last_checked and set it to the current date and
    # time in the format YYYY-MM-DD HH
    df["last_checked"] = pd.to_datetime("today").strftime("%Y-%m-%d %H")
    # remove the item where name is Dev Mode v2
    df = df[df["name"] != "Dev Mode v2"]

    df.to_html(
        "/root/github_repos/gpt_jailbreak_status/gpt_jb.html",
        index=False)

    # write the tabulated dataframe to a file
    with open("/root/github_repos/gpt_jailbreak_status/gpt_jb.txt", "w") as f:
        f.write(tabulate(df, headers="keys", tablefmt="psql"))

    # write the dataframe to a csv file
    df.to_csv(
        "/root/github_repos/gpt_jailbreak_status/gpt_jb.csv",
        index=False)

    # in the html file write at the top of the file three lines of text

    # <h1> GPT-3 Jailbreak Status </h1>
    # <h2> Last Checked: {date} </h2>
    # <h2> Total Jailbreaks: {number} </h2>

    with open("/root/github_repos/gpt_jailbreak_status/gpt_jb.html", "r") as f:
        html = f.read()

    with open("/root/github_repos/gpt_jailbreak_status/gpt_jb.html", "w") as f:
        f.write(f"<h1> GPT-3 Jailbreak Status </h1>\n")
        f.write(
            f"<h2> Last Checked: {pd.to_datetime('today').strftime('%Y-%m-%d %H:%M')} </h2>\n")
        f.write(f"<h2> Total Jailbreaks: {len(df)} </h2>\n")
        f.write(f"<h2> ETH Address: 0x01d23570c34A78380452A4BE9C95bAe439719bAf </h2>\n")
        f.write(f"<h2> BTC Address: 3QjWqhQbHdHgWeYHTpmorP8Pe1wgDjJy54 </h2>\n")
        f.write(f"<h2> Twitter: @James12396379 </h2>\n")

        table_content = '''
        <table>
        <tr>
            <th>Name</th>
            <th>Donation</th>
        </tr>
        <tr>
            <td>Jacob Parker (TechSavvy_23)</td>
            <td>&#16315.00</td>
        </tr>
        <tr>
            <td>Emily Brown</td>
            <td>0.00009 BTC</td>
        </tr>
        <tr>
            <td>Michael Green (@AlgoAce12)</td>
            <td>&#16310.00</td>
        </tr>
        <tr>
            <td>Sarah Wilson</td>
            <td>0.00007 BTC</td>
        </tr>
        </table>
        '''

        f.write("\n\n\n" + table_content + "\n\n\n")

        f.write(html)

    # run the git commands to push the changes to github
    # cd /root/github_repos/gpt_jailbreak_status
    # git add .
    # git commit -m "update"
    # git push


if __name__ == "__main__":
    main()
