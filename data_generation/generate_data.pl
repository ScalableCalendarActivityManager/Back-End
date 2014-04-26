#!/usr/bin/perl -w
use strict;

my $nextID = 0;

use Inline Spew => <<'SPEW_GRAMMAR';
START: SingleEvent | CleanEtcEvent
SingleEvent: "Meeting" | "Birthday party" | "Dentist appointment" | "Doctor's appointment" | "Jury duty" | "Graduation party" | "Interview" | "Conference call" | "Watch the movie" | "Eat dinner" | "Brush teeth" | "Take out the trash" | "Do homework" | "Eat breakfast" | "Eat a donut" | "Drink coffee" | "Submit application" | "Make business phone call" | "Pick up package" | "Go for a run" | "Go to the gym" | "Go for a swim" | "Go hiking" | "Take a nap" | "Visit grandparents" | "Go to the bank" | "Buy groceries" | "Do laundry" | "Take shower" | "Eat lunch" | "Get a haircut" | "Go to concert" | "Go to airport" | "Go to train station" | "Mow lawn" | "Go fishing" | "Aerobics class" | "Yoga" | "Cooking class" | "Town hall meeting" | "Study" | "Host friends for dinner" | "Run marathon" | "Go to football game" | "Go to basketball game" | "Go on date" | "Go to circus" | "Go to zoo" | "Acting class" | "Participate in " protest " protest downtown."
protest: "pollution" | "minimum-wage" | "processed foods" | "technology" | "large corporation" | "Wall Street"
CleanEtcEvent: Action " " item
Action: "Clean" | "Buy" | "Rent" | "Sell" | "Fix"
item: "garage" | "bathroom" | "car" | "boat" | "TV" | "refrigerator" | "closet" | "desk" | "table" | "dining room" | "office" | "classroom"
SPEW_GRAMMAR

srand(0);

my @movies = ();
my @names = ();
my @calendar_types = ("Leisure", "School" , "Work");
my @email_addrs = ("msn.com", "vanderbilt.edu", "yahoo.com", "gmail.com");
my @locations = ("Vanderbilt", "Home", "Downtown", "Rand", "Featheringill",
                 "East Nashville", "West End", "Towers", "Alumni Lawn",
                 "Commons");
my @invite_status = ("Accepted", "Undecided");

my %users = ();
my @calendars = ();

sub print_calendar (\% \%) {
    my $calendarReference = shift;
    my $users = shift;
    my $result = "{\n";
    $result .= "\t\"ID\":" . $calendarReference->{"id"} . ",\n";
    $result .= "\t\"name\":\"" . $calendarReference->{"name"} . "\",\n";
    $result .= "\t\"owners\":[\n";
    
    foreach my $owner (@{$calendarReference->{"owner"}}) {
        my $can_write = "false";
        
        foreach my $able_to_write (@{$calendarReference->{"can_write"}}) {
            if ($able_to_write eq $owner) {
                $can_write = "true";
                last;
            }
        }
        
        $result .= "\t\t{\n";
        $result .= "\t\t\"ID\":" . $users->{$owner}->{"id"} . ",\n";
        $result .= "\t\t\"username\":\"" . $users->{$owner}{"username"}
                   . "\",\n";
        $result .= "\t\t\"can_write\":$can_write\n";
        $result .= "\t\t},\n";
    }
    
    chop $result; chop $result; $result .= "\n";
    
    $result .= "\t],\n";

    $result .= "\t\"events\":[\n";    
        
    foreach my $event (@{$calendarReference->{"events"}}) {
        $result .= "\t\t{\n";
        $result .= "\t\t\"ID\":" . $event->{"id"} . ",\n";
        $result .= "\t\t\"name\":\"" . $event->{"name"} . "\",\n";
        $result .= "\t\t\"startTime\":\"" . $event->{"startTime"} . "\",\n";
        $result .= "\t\t\"endTime\":\"" . $event->{"endTime"} . "\",\n";
        $result .= "\t\t\"location\":\"" . $event->{"location"} . "\",\n";
        $result .= "\t\t\"owner\":\"" . $users->{$event->{"owner"}}{"username"}
                   . "\",\n";
        $result .= "\t\t\"invitees\":[\n";
        
        
        foreach my $invitee (@{$event->{"invitees"}}) {
            $result .= "\t\t\t{\n";
            $result .= "\t\t\t\"ID\":" . $users->{$invitee}->{"id"} . ",\n";
            $result .= "\t\t\t\"username\":\"" . $users->{$invitee}{"username"}
                       . "\"\n";
            $result .= "\t\t\t},\n";
        }
        
        if (scalar(@{$event->{"invitees"}}) > 0) {
            chop $result; chop $result; $result .= "\n";
        }
        
        $result.= "\t\t]\n";
        
        $result .= "\t\t},\n";
    }
    
    chop $result; chop $result; $result .= "\n";
    
    $result .= "\t],\n";
    $result .= "\t\"isPrivate\":" 
               . ($calendarReference->{"is_private"} ? "true" : "false") . "\n";
    $result .= "}\n";

    return $result;
}

sub print_user(\$ \%) {
    my $user = shift;
    my $users = shift;
    
    my $calendars = $users->{$$user}{"calendars"};
    
    my $result = "{\n";
    
    $result .= "\t\"ID\":" . $users->{$$user}{"id"} . ",\n";
    $result .= "\t\"username\":\"" . $users->{$$user}->{"username"} . "\",\n";
    $result .= "\t\"name\":\"" . $$user . "\",\n";
    $result .= "\t\"password\":\"" . $users->{$$user}{"pass"} . "\",\n";
    $result .= "\t\"calendars\":[\n";
    
    foreach my $calendar (@{$calendars}) {
        $result .= "\t\t{\n";
        
        $result .= "\t\t\t\"ID\":" . $calendar->{"id"} . ",\n";
        $result .= "\t\t\t\"name\":\"" . $calendar->{"name"} . "\"\n";
        
        $result .= "\t\t},\n";
    }
    chop $result; chop $result; $result .= "\n";
    
    $result .= "\t],\n";
    
    $result .= "\t\"owned_events\":[\n";
    
    foreach my $event (@{$users->{$$user}{"owned_events"}}) {
        $result .= "\t\t{\n";
        
        $result .= "\t\t\t\"ID\":" . $event->{"id"} . ",\n";
        $result .= "\t\t\t\"name\":\"" . $event->{"name"} . "\"\n";
        
        $result .= "\t\t},\n";
    }
    chop $result; chop $result; $result .= "\n";
    $result .= "\t],\n";
    
    $result .= "\t\"invited_events\":[\n";
    
    foreach my $event (@{$users->{$$user}{"invited_events"}}) {
        $result .= "\t\t{\n";
        
        $result .= "\t\t\t\"ID\":" . $event->{"id"} . ",\n";
        $result .= "\t\t\t\"name\":\"" . $event->{"name"} . "\",\n";
        my $status = $invite_status[int(rand(@invite_status))];
        $result .= "\t\t\t\"status\":\"" . $status . "\"\n";
        
        if ($status eq "Accepted") {
            chop $result; $result .= ",\n";
            
            $result .= "\t\t\t\"calendar\":\"" 
                       . $calendars->[int(rand(@{$calendars}))]->{"name"}
                       . "\"\n";
        }
        
        $result .= "\t\t},\n";
    }
    if (scalar(@{$users->{$$user}{"invited_events"}}) > 0) {
        chop $result; chop $result; $result .= "\n";
    }
    
    $result .= "\t]\n";
    
    $result .= "}\n";

    return $result;
}

sub generate_event(\@) {
    my $user = shift;
    my $result = spew();
    if ($result eq "Watch the movie") {

        $result .= " '" . random_movie() . "'";
    }
       
    my $time = generate_time();
    my $start = format_time(\$time);
    # End is at most 8 hours in future
    my $timeIncrement = $time + int(rand(28800));
    my $end = format_time(\$timeIncrement);
    my $location = $locations[int(rand(@locations))];
    
    my @invitee_list = ();
    
    my @user_names = keys %users;

    RANDOM_NAME: for (my $i = 0; $i < int(rand(5)); $i++) {
        my $rand_name = $user_names[int(rand(@user_names))];
        
        foreach my $curName (@invitee_list) {
            if ($rand_name eq $curName) {
                next RANDOM_NAME;
            } 
        }
        
        if ($rand_name eq $user->[0]) {
            next RANDOM_NAME;
        }
        
        
        push @invitee_list, $rand_name;
    }
    
    return {
         id => $nextID++,
         name => $result,
         startTime => $start,
         endTime => $end,
         location => $location,
         owner => $user->[0],
         invitees => \@invitee_list
    };
}


open(MOVIE_FILE, "<filtered_movies.txt") || die "Could not load movie file.";
while (<MOVIE_FILE>) {
    chomp;
    s/ $//;
    
    push @movies, $_;
}
close(MOVIE_FILE);


open(NAMES_FILE, "<word_list_moby_given_names_english.flat.txt") || 
    die "Could not load names.";
while (<NAMES_FILE>) {
    chop;
    chop;
    push @names, $_;
}
close(NAMES_FILE);



print "Number of users to generate: ";
my $numUsers = <>;
chomp $numUsers;
print "Mode (calendars | users): ";
my $mode = <>;
chomp $mode;

# Generate users
for (my $i = 0; $i < $numUsers; $i++) {
    my $newName = generate_name();
    $newName =~ /(\w+) (\w+)/;
    my $username = lc($1) . "." . lc($2) . "\@vanderbilt.edu";
    
    if (!(exists $users{$newName})) {
        $users{$newName} = {id => $nextID++, username => $username,
                            pass => generate_password(), 
                            calendars => [], invited_events => []};
    }
}

print "Generated " . int(keys %users) . " users.\n";

# Generate calendars for each user
foreach my $user (keys %users) {
    my $selectionMask = int(rand(7)) + 1;
    
    if ($selectionMask & 0x1) {
        my %newCal = (id => $nextID++, name => $calendar_types[0], 
                      owner => [$user], can_write => [$user], events => [],
                      is_private => int(rand(2)));
        push @calendars, \%newCal;
        push $users{$user}->{"calendars"}, \%newCal;
    }
    if ($selectionMask & 0x2) {
        my %newCal = (id => $nextID++, name => $calendar_types[1], 
                      owner => [$user], can_write => [$user], events => [],
                      is_private => int(rand(2)));
        push @calendars, \%newCal;
        push $users{$user}->{"calendars"}, \%newCal;
    }
    if ($selectionMask & 0x4) {
        my %newCal = (id => $nextID++, name => $calendar_types[2], 
                      owner => [$user], can_write => [$user], events => [],
                      is_private => int(rand(2)));
        push @calendars, \%newCal;
        push $users{$user}->{"calendars"}, \%newCal;
    }
}

# Generate events for each calendar and add other potential owners
foreach my $calendar (@calendars) {
    my $event = generate_event(@{$calendar->{"owner"}});
    
    push @{$users{$calendar->{"owner"}[0]}->{"owned_events"}}, $event;
    
    foreach my $user (@{$event->{"invitees"}}) {
        push @{$users{$user}->{"invited_events"}}, $event;
    }
    
    push $calendar->{"events"}, $event;
    
    RANDOM_NAME: for (my $i = 0; $i < int(rand(6)); $i++) {
        my @user_names = keys %users;
        my $rand_name = $user_names[int(rand(@user_names))];
        
        foreach my $curName (@{$calendar->{"owner"}}) {
            if ($rand_name eq $curName) {
                next RANDOM_NAME;
            } 
        }
        
        
        push @{$calendar->{"owner"}}, $rand_name;
        
        if (int(rand(2)) == 1) {
            push @{$calendar->{"can_write"}}, $rand_name;
        }
    }
}

if ($mode eq "calendars") {
    foreach my $calendar (@calendars) {
        print print_calendar(%{$calendar}, %users);
    }
} elsif ($mode eq "users") {
    foreach my $user (sort keys %users) {
        print print_user($user, %users);
    }
} else {
    print "Unrecognized mode: $mode\n";
}



sub random_movie {
    my $result = $movies[int(rand(@movies))];
    
    return $result;
}


sub generate_name {
    my $result = "$names[rand(@names)] $names[rand(@names)]";

    return $result;
}


sub generate_password {
    my $pass_string = 'abcdefghijkmnpqrstuvwxyz23456789' .
                      'ABCDEFGHJKLMNPQRSTUVWXYZ$#@%';
    
    my $password = "";
    
    for (my $j = 0; $j < 10; $j++) {
        $password .= substr($pass_string, (int(rand(length($pass_string)))), 1);
    }
    
    return $password;
}

sub format_time(\$) {
    my $random_time = shift;    

    my ($sec,$min,$hour,$mday,$mon,
        $year,$wday,$yday,$isdst) = localtime $$random_time;
    
    $year += 1900;
        
    $mon += 1;
    
    if ($sec < 10) {
        $sec = "0" . $sec;
    }
    
    if ($min < 10) {
        $min = "0" . $min;
    }
    
    if ($hour < 10) {
        $hour = "0" . $hour;
    }
    
    if ($mday < 10) {
        $mday = "0" . $mday;
    }
    
    if ($mon < 10) {
        $mon = "0" . $mon;
    }
    
    return "$year-$mon-$mday $hour:$min:$sec";
}

sub generate_time {
    # Generate random times starting from May 12, 2014 at 8:00 AM CDT and going
    # 90 days in the future
    
    return int(rand(7776000)) + 1399899600;
}

