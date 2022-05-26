from enum import Enum


class ManeuverType(Enum):
    Invalid = 0  # no valid turn instruction
    NewName = 1  # no turn, but name changes
    Continue = 2  # remain on a street
    Turn = 3  # basic turn
    Merge = 4  # merge onto a street
    OnRamp = 5  # special turn (highway ramp on-ramps)
    OffRamp = 6  # special turn, highway exit
    Fork = 7  # fork road splitting up
    EndOfRoad = 8  # T intersection
    Notification = 9  # Travel Mode Changes, Restrictions apply...
    EnterRoundabout = 10  # Entering a small Roundabout
    EnterAndExitRoundabout = 11  # Touching a roundabout
    EnterRotary = 12  # Enter a rotary
    EnterAndExitRotary = 13  # Touching a rotary
    EnterRoundaboutIntersection = 14  # Entering a small Roundabout
    EnterAndExitRoundaboutIntersection = 15  # Touching a roundabout

    # Values below here are silent instructions
    NoTurn = 17  # end of segment without turn/middle of a segment
    Suppressed = 18  # location that suppresses a turn
    EnterRoundaboutAtExit = 19  # Entering a small Roundabout at a countable exit
    ExitRoundabout = 20  # Exiting a small Roundabout
    EnterRotaryAtExit = 21  # Enter A Rotary at a countable exit
    ExitRotary = 22  # Exit a rotary
    EnterRoundaboutIntersectionAtExit = 23  # Entering a small Roundabout at a countable exit
    ExitRoundaboutIntersection = 24  # Exiting a small Roundabout
    StayOnRoundabout = 25  # Continue on Either a small or a large Roundabout
    Sliproad = 26  # Something that looks like a ramp, but is actually just a small sliproad
    MaxTurnType = 27  # Special value for static asserts
