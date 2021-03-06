import click
import requests

from yellowcabs.helpers import download
from yellowcabs.helpers import get_url
from yellowcabs import processing as p


@click.command()
@click.argument("year-month", type=click.DateTime(formats=["%Y-%m"]), required=1)
@click.pass_context
def average_trip_duration(ctx, year_month):
    """Calculate the average NY yellow cab trip duration in YYYY-MM"""
    url = get_url(year_month)
    try:
        fname = download(url)
    except requests.exceptions.RequestException as e:
        click.echo(f"{e}")
        ctx.abort()
    df = (
        p.load_csv(fname)
        .pipe(p.rename_columns)
        .pipe(p.filter_by_month_year, dt=year_month)
        .pipe(p.calculate_durations)
        .pipe(p.reindex_on_pickup)
        .pipe(p.monthly_average_durations)
    )
    duration = int(round(df["duration"][0]))
    click.echo(
        f"The average trip duration in "
        f"{year_month.month:02d}/{year_month.year} was {duration} seconds."
    )
