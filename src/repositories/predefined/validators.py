import datetime

import dateutil.rrule
import icalendar


def validate_calendar(calendar: icalendar.Calendar):
    unique_ids = set()
    for event in calendar.walk("VEVENT"):
        event: icalendar.Event
        validate_vevent(event)

        uid = event["UID"]
        if uid in unique_ids:
            raise ValueError(f"Event UID ({uid}) is not unique", event)

        unique_ids.add(uid)


def validate_vevent(event: icalendar.Event):
    if "UID" not in event:
        raise ValueError("Event has no UID", event)
    #
    # if "DTSTAMP" not in event:
    #     raise ValueError("Event has no DTSTAMP", event)

    vddd_dtstart: icalendar.vDDDTypes | None = event.get("DTSTART")
    vddd_dtend: icalendar.vDDDTypes | None = event.get("DTEND")
    vddd_duration: icalendar.vDDDTypes | None = event.get("DURATION")

    if not vddd_dtstart:
        raise ValueError("Event has no DTSTART", event)

    if not vddd_dtend and not vddd_duration and vddd_dtstart.params.get("VALUE") != "DATE":
        raise ValueError("Event has no DTEND or DURATION", event)

    if vddd_dtend and vddd_duration:
        raise ValueError("Event has both DTEND and DURATION", event)

    if vddd_dtend and vddd_dtstart.dt > vddd_dtend.dt:
        raise ValueError("DTSTART is later than DTEND", event)

    if "RRULE" in event:
        # should be compatible with dtstart
        rrule: dateutil.rrule.rrule = dateutil.rrule.rrulestr(
            event["RRULE"].to_ical().decode(), dtstart=vddd_dtstart.dt
        )
        rrule_dates = rrule.__iter__()
        rrule_first_dt = next(rrule_dates)

        if rrule_first_dt:
            rrule_first_date = rrule_first_dt.date()

            if isinstance(vddd_dtstart.dt, datetime.datetime):
                vdd_date = vddd_dtstart.dt.date()
            elif isinstance(vddd_dtstart.dt, datetime.date):
                vdd_date = vddd_dtstart.dt
            else:
                raise ValueError("DTSTART is not datetime or date", event)

            if rrule_first_date != vdd_date:
                raise ValueError("DTSTART is not compatible with RRULE", event)
