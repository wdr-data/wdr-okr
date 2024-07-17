from datetime import timedelta

import pandas as pd
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from loguru import logger

from okr.models import Insta, InstaInsight

# from okr.models import Podcast


def _convert_tz_aware_to_naive(df):
    """
    Convert all datetime-aware columns to Berlin time,
    then make them timezone-naive (for Excel compatibility)
    """
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            # Ensure the column has timezone-aware datetimes
            if df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_convert("Europe/Berlin").dt.tz_localize(None)
            else:
                # If the datetime is naive, assume it's UTC and localize to Berlin
                df[col] = (
                    df[col]
                    .dt.tz_localize("UTC")
                    .dt.tz_convert("Europe/Berlin")
                    .dt.tz_localize(None)
                )

    return df


def _get_insights_df(insta):
    """Get all insights from the past year for an insta object and return them
    as a pandas dataframe
    """
    # get all InstaInsight for insta object and with date in the last 365 days
    insights = InstaInsight.objects.filter(
        Q(insta=insta) & Q(date__gte=timezone.now() - timedelta(days=365))
    )

    # convert insights to pandas dataframe
    df_insights = pd.DataFrame(list(insights.values()))

    # Automatically find and convert all datetime-aware columns to Berlin time,
    # then make them timezone-naive (for Excel compatibility)
    df_insights = _convert_tz_aware_to_naive(df_insights)

    return df_insights


def generate_xlsx(request, id):
    """
    Generate an XLSX analytics file for the podcast with the given ID

    Parameters:
    - request: The HTTP request object
    - id: The ID of the podcast to generate the XLSX for

    Returns:
    - An HTTP response containing the generated XLSX file
    """

    logger.info(f"Generate XLSX for {id}")

    # Check API key
    secret_key = request.GET.get("secret_key")
    if secret_key != settings.XLSX_SECRET_KEY or not settings.XLSX_SECRET_KEY:
        return HttpResponse("Unauthorized", status=401)

    # Check if supplied ID is a valid integer
    try:
        id = int(id)
    except ValueError:
        return HttpResponse("Invalid ID", status=400)

    # Get the podcast with the id
    try:
        insta = Insta.objects.get(id=id)
    except Insta.DoesNotExist:
        return HttpResponse("Not found", status=404)

    df_insights = _get_insights_df(insta)

    # Create an HTTP response with the appropriate Excel header
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{insta.id}.xlsx"'

    # Create a Pandas Excel writer using the response as the file
    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df_insights.to_excel(writer, sheet_name="Insights", index=False)
        # df_followers.to_excel(writer, sheet_name='followers', index=False)
        # df_data_demographics.to_excel(writer, sheet_name='demographics', index=False)

    logger.info(f"XLSX for {id} generated successfully.")

    # Return the response containing the Excel file
    return response

    # return HttpResponse(f"Generated XLSX: {id} for {insta.name}")
