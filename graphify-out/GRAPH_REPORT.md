# Graph Report - Companion-Forever  (2026-09-21)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 6881 nodes · 15843 edges · 268 communities (234 shown, 34 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 775 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `06cc8d3a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- HeroButton
- theme
- restyle
- test_character_sheet.py
- test_install_failure.py
- MockRaidDataProvider
- RaidDataService
- test_academy_progression.py
- companion_manager.py
- test_replay.py
- parse_schedule
- test_raid_data_service.py
- test_addon_payloads.py
- test_character_links.py
- Actor
- CooldownUsage
- test_live_updates.py
- wow_clients.py
- test_academy_evaluator.py
- AcademyService
- test_addon_analysis_sync.py
- AnalysisView
- analyzer/models.py
- warcraftlogs_payload.py
- preparation.py
- test_theme_connections.py
- test_raid_context.py
- snapshot_from_payload
- test_access_profile.py
- Paths
- CompanionManager
- test_raid_center.py
- FightSummary
- test_discord_links.py
- LoadingCard
- test_greeting.py
- DiscordAccountStore
- RaidSnapshot
- test_academy_history_card.py
- test_last_pull.py
- OverviewPage
- test_analysis_guide.py
- UptimeEntry
- CharacterLinksPage
- LogWidget
- OverlayWindow
- test_addon_inbox.py
- test_character_report_sync.py
- raid_schedule.py
- test_update_banner.py
- NavColumn
- Card
- test_roster_card.py
- RaidCenterPage
- test_academy_selection.py
- test_lesson_catalog.py
- test_changelog.py
- classes/_common.py
- test_discord_app.py
- MainWindow
- test_live_bridge.py
- test_academy_checks.py
- academy/models.py
- Resources
- StatusDot
- RosterStrip
- player_abilities.py
- test_quick_actions.py
- test_loading_progress.py
- checks.py
- test_academy_service.py
- test_names.py
- GitHubUpdater
- test_net_errors.py
- test_archive_browser.py
- test_raid_schedule_special.py
- test_academy_empty_state.py
- test_appearance_section.py
- test_overview_header.py
- Runtime
- parse_character_sheet
- test_discord_auth.py
- AddonPage
- discord_app.py
- RaidContext
- FakeService
- PullRecord
- test_warcraftlogs_provider.py
- test_backup_saved_variables.py
- LearnView
- SetupWizard
- test_damage_analysis.py
- test_discord_section.py
- test_tokens.py
- TitleBar
- test_academy_dummy_sync.py
- storage_usage.py
- Rating
- check_version.py
- test_character_links_page.py
- FakeService
- find_combat_log
- sync_manager.py
- test_character_links_raid_choice.py
- test_storage_usage.py
- resolve
- LiveView
- SplashScreen
- init_theme
- ArchiveBrowser
- quote_lua_string
- test_archive_index.py
- test_backend_config.py
- CompanionUpdater
- _pull_snapshot
- class_abilities.py
- specs.py
- test_startup_popups.py
- PulseClock
- test_class_avatar.py
- RaidDataProvider
- changelog_source.py
- test_tour.py
- test_task_card.py
- mock_schedule.py
- archive_index.py
- _snapshot
- avoidable.py
- StorageWatch
- raid_context.py
- test_class_abilities.py
- test_update_visibility.py
- WarcraftLogsProvider
- BackupsSection
- extract_variable_body
- SourceView
- NavigationItem
- _Row
- RaidContextHeader
- SyncReader
- data/encounters.py
- test_buff_uptimes.py
- RaidDay
- RaidSchedule
- ._announce_storage
- DiscordSection
- ThemeManager
- test_last_pull_card.py
- test_spec_table.py
- academy_dummy_sync.py
- pytest
- _run
- Autostart
- Skeleton
- known_encounters
- read_changelog_sections
- WarcraftLogsArchiveClient
- _Swatch
- nav
- build_report_list
- WhatsNewDialog
- test_motion.py
- damage.py
- LessonResult
- FetchResult
- best_try
- ReplayState
- _render_emphasis
- ModulesSection
- page
- encounter_meta
- Trend
- match
- CharactersPage
- _Logger
- AddonReader
- for_actor
- build_movement
- verdict
- bot_url_override_path
- backup.py
- UpdateWatch
- pulse_clock
- LastPullCard
- UpdateRow
- UpdateCard
- MeterRowList
- _Logger
- test_addon_repository.py
- weakest_of
- build_fight_list
- AccessProfileSync
- normalize_bot_url
- .__init__
- SectionCard
- BossBar
- _Logger
- test_a_source_without_a_timeline_offers_no_replay
- _hits_payload
- _announce
- report_subtitle
- group_reports_by_day
- selection_text
- test_the_popups_are_queued_once_not_on_every_restore
- _ArtworkHeader
- ToastHost
- focus_placeholder
- _Logger
- _Logger
- test_restart_does_not_leave_a_second_worker_behind
- ring_alpha
- _Logger
- translations
- ._refresh_updates
- .metric
- page
- _theme
- _warn_subscribers
- AreaFocus
- build_metrics
- class_name
- main
- .newest_with_saved_variables
- show_whats_new_if_needed
- AttentionEffect
- should_animate_number
- .motion_reduced
- .apply_stylesheet
- known_specs
- .time_label
- analysis_guide.py
- .browsing
- .academy
- show_tour
- .show_lesson
- suspend_value_animation
- accent
- _Summary
- test_a_stale_fights_result_is_discarded
- Enum
- _DialogPage
- tinted
- test_the_day_is_named_relative_to_today
- _shutdown_services
- qt_app
- _State
- _line
- analysis/__init__.py
- data/__init__.py
- _duration
- pages/raid/__init__.py
- installed_families
- is_available
- clear_cache
- MotionToken
- density
- TypeToken
- widgets/academy/__init__.py
- widgets/raid/__init__.py
- tv/__init__.py
- AppRun
- updater.sh
- build_appimage.sh
- build_linux.sh
- test_the_source_is_registered_in_the_service

## God Nodes (most connected - your core abstractions)
1. `RaidSnapshot` - 208 edges
2. `restyle()` - 125 edges
3. `theme()` - 116 edges
4. `font()` - 112 edges
5. `MockRaidDataProvider` - 93 edges
6. `HeroButton` - 78 edges
7. `Colors` - 75 edges
8. `Actor` - 74 edges
9. `Paths` - 73 edges
10. `parse_schedule()` - 71 edges

## Surprising Connections (you probably didn't know these)
- `replay_state()` --calls--> `ReplayState`  [INFERRED]
  tests/test_academy_empty_state.py → core/raid_state.py
- `replay_state()` --calls--> `ReplayState`  [INFERRED]
  tests/test_analysis_guide.py → core/raid_state.py
- `test_page_ids_are_unique()` --uses--> `PageId`  [INFERRED]
  tests/test_navigation.py → gui/navigation.py
- `archive_state()` --calls--> `ArchiveState`  [INFERRED]
  tests/test_academy_empty_state.py → core/raid_state.py
- `__init__()` --calls--> `ArchiveState`  [INFERRED]
  tests/test_analysis_guide.py → core/raid_state.py

## Import Cycles
- None detected.

## Communities (268 total, 34 thin omitted)

### Community 0 - "HeroButton"
Cohesion: 0.02
Nodes (92): core, is_linux(), Zentrale Bezugsquelle für Raid-Daten. Dies ist der einzige Ort, an dem die…, dataclasses, DiscordLinkPromptDialog, QDialog, Wird einmal beim Start aufgerufen (siehe gui/main_window.py), nach dem "Was ist…, Start-Hinweis, solange kein Discord-Account verknüpft ist. Schließbar wie jeder… (+84 more)

### Community 1 - "theme"
Cohesion: 0.06
Nodes (89): app_url(), Dieselbe Adresse für die Discord-Anwendung statt für den Browser. Der Knopf…, is_usable(), Ob mit dieser Ablage tatsächlich etwas beim Bot abgerufen werden kann. Die…, faulthandler, Ein Update auslösen - an einer Stelle für alle Knöpfe. **Warum es das gibt.**…, Die Änderungsansicht: was sich in welcher Fassung geändert hat. **Warum sie…, Der Wegweiser: was ist WeintTV, was die Academy, was das Archiv - und was muss… (+81 more)

### Community 2 - "restyle"
Cohesion: 0.03
Nodes (55): is_demo_source(), ChangelogDialog, QDialog, QFrame, Beide Komponenten, alle Fassungen., Kein Changelog gefunden - und dazu, warum. Beim Addon ist die häufige Ursache…, Eine Fassung: Nummer, Datum, Zustand, Text. Der Zustand ist die eigentliche…, _VersionBlock (+47 more)

### Community 3 - "test_character_sheet.py"
Cohesion: 0.03
Nodes (82): Der Ablageschlüssel eines Charakters. Bewusst `Name-Realm` und nicht nur der…, sheet_key(), archive_key(), belongs_to(), CharacterStore, default_min_level(), is_high_level(), Die Mindeststufe, solange niemand eine eigene eingetragen hat. Sie kommt aus… (+74 more)

### Community 4 - "test_install_failure.py"
Cohesion: 0.04
Nodes (76): _chain(), in_protected_location(), InstallPermissionError, InstallTargetError, is_permission_error(), missing_target_message(), permission_message(), probe_writable() (+68 more)

### Community 5 - "MockRaidDataProvider"
Cohesion: 0.04
Nodes (56): CombatEvent, ConsumableState, DeathEntry, Ein Tod innerhalb des laufenden Pulls., Verbrauchsgegenstände (Flask, Bufffood, Kampftrank). `missing` listet die Namen…, Ein sonstiges Kampfereignis mit Zeitpunkt. Bewusst frei gehalten (`kind` als…, _build_actors(), MockRaidDataProvider (+48 more)

### Community 6 - "RaidDataService"
Cohesion: 0.04
Nodes (35): QObject, RaidDataService, Lädt einen einzelnen Fight und macht ihn zum angezeigten Snapshot - der…, Der Eintrag der Pull-Liste zu dieser Auswahl, oder None. Nur unter gehaltenem…, Nur unter gehaltenem Lock aufrufen., Ob für die aktuelle Auswahl überhaupt eine Wiedergabe in Frage kommt - im…, Startet die Wiedergabe des gerade gewählten Pulls. Zwei Wege, ein Ziel: im…, Holt die Zeitleiste eines Pulls im Voraus, ohne sie abzuspielen. Der Grund ist… (+27 more)

### Community 7 - "test_academy_progression.py"
Cohesion: 0.05
Nodes (80): _progress(), Die Lernkurve in der Form, in der das Addon sie zeichnet. **Gerechnet wird hier…, plan_order(), Die Bereiche in der Reihenfolge, in der der Plan sie abarbeitet. Ohne `focus`…, build_focus(), build_trend(), category_sentence(), focus_note() (+72 more)

### Community 8 - "companion_manager.py"
Cohesion: 0.05
Nodes (44): day_from_iso(), Die Ablage der Lernkurve. Die HTTP-lose Schwester von…, Der heutige Tag als "JJJJ-MM-TT" - der Raidtag eines Live-Pulls. Eigene…, Der Raidtag eines Berichts, aus seinem Zeitstempel. Der Bot nennt ihn in UTC;…, today(), Die WeintAcademy auf Anwendungsebene. Der Service macht drei Dinge und sonst…, Stellt dem Addon das Zugriffsprofil zu (WeintCodex ab 1.2.0.0). Der Bot kennt…, AppState (+36 more)

### Community 9 - "test_replay.py"
Cohesion: 0.05
Nodes (65): analyzer_replay, Wiedergabe eines abgeschlossenen Kampfes. Dies ist die eine, bewusst eng…, AvoidableHit, FightTimeline, PlayerSeries, Datenmodell der Wiedergabe. Alle Zeitreihen sind **kumulativ**, nicht als…, Der vollständige Verlauf eines Kampfes. `aggregate` ist der Gesamtschnappschuss…, Ob sich daraus überhaupt eine Wiedergabe bauen lässt. (+57 more)

### Community 10 - "parse_schedule"
Cohesion: 0.05
Nodes (74): composition_text(), countdown_text(), open_slots(), others_text(), parse_schedule(), Der Satz unter den Streifen. "Vier offene Plätze · 1 Tank, 1 Heiler, 2 frei…, Die Zeile über die weiteren gleichzeitig laufenden Raids. "Außerdem offen: 25er…, Die Antwort von `/companion/raid-schedule` einlesen. Defensiv wie… (+66 more)

### Community 11 - "test_raid_data_service.py"
Cohesion: 0.05
Nodes (69): _FakeArchiveClient, _make_service(), Die Live/Archiv-Zustandsmaschine des RaidDataService. core/raid_data_service.py…, Ohne diesen Weg wäre die Wiedergabe erst vorführbar, sobald der Bot den…, Der Fehler, der die Wiedergabe unbedienbar machte. Die Zeitleiste wird in einem…, Sonst spielt der Wiedergabe-Knopf den vorherigen Kampf ab. `start_replay()`…, Ein zweiter Druck auf Wiedergabe spult zurück - und muss den Modus wieder…, Der Grund, aus dem der Wiedergabe-Knopf im Live-Modus unsichtbar blieb.… (+61 more)

### Community 12 - "test_addon_payloads.py"
Cohesion: 0.07
Nodes (57): _ability(), build_academy_catalog(), build_academy_state(), build_weinttv_report(), _gap(), _identity(), Die Auswertung in der Form, in der das Addon sie liest. WeintTV und die Academy…, Der Pull-Bericht für den WeintTV-Tab im Addon. `player_name` ist der Charakter,… (+49 more)

### Community 13 - "test_character_links.py"
Cohesion: 0.05
Nodes (57): class_label(), _detail_of(), Ordnet einem Discord-Account einen Charakter zu. `discord_id` reist als…, Entfernt eine Zuordnung. Ohne `class_token` fallen **alle** Handeinträge dieses…, Ergebnis eines Schreibvorgangs., Liefert (status, body, reason). `status` ist -1 bei einem Netzwerkfehler,…, WriteResult, format_character() (+49 more)

### Community 14 - "Actor"
Cohesion: 0.06
Nodes (59): _clock(), _combine(), _comparison_group(), find_actor(), _find_entry(), _first_mechanic_moment(), _join(), _mechanics_of() (+51 more)

### Community 15 - "CooldownUsage"
Cohesion: 0.04
Nodes (53): alignment_of(), burst_alignment(), category_of(), counts_towards_usage(), is_major(), possible_uses(), Cooldown-Nutzung: eine Rechnung je Frage. Diese Datei ist die Antwort auf vier…, Ob ein Cooldown in die Quote "genutzt von möglich" gehört. Nur Cooldowns, die… (+45 more)

### Community 16 - "test_live_updates.py"
Cohesion: 0.05
Nodes (52): Wie viele Sekunden bis zum nächsten Abruf. Rein und ohne Netz, aus demselben…, refresh_interval(), _Github, _Logger, _payload(), Kommt an, was im Hintergrund gefunden wird? Zwei Auskünfte der Übersicht wurden…, `is_running()` zieht die hintere Grenze: solange gespielt wird, ändern sich…, Ein `RaidScheduleSync` mit verknüpftem Konto, eigenem Zwischenspeicher-… (+44 more)

### Community 17 - "wow_clients.py"
Cohesion: 0.06
Nodes (57): Sucht die Installation einer Spielversion auf der Platte. Bis 4.0 suchte diese…, all_clients(), client(), client_label(), default_client(), foreign_flavor_folders(), is_known_client(), Welche Spielversion diese App bedient. Seit 5.0 gibt es nur noch eine: *World… (+49 more)

### Community 18 - "test_academy_evaluator.py"
Cohesion: 0.07
Nodes (60): build_plan(), _evaluate(), _item(), build_profile(), Baut das Lernprofil eines Spielers aus einem Snapshot. Ist der Spieler nicht…, Leitet aus einem Profil die nächsten Lektionen ab und prüft sie gegen den…, Alle Spielernamen eines Snapshots, alphabetisch - die Auswahl, die die Academy…, roster_names() (+52 more)

### Community 19 - "AcademyService"
Cohesion: 0.06
Nodes (27): match_name(), Den passenden Eintrag aus `names` finden und **in dessen Schreibweise**…, AcademyService, Dieselben Serien, aber ohne einen Eintrag anzulegen - für Leser (Anzeige,…, Wählt eine Lektion für den Trainingsplan ab oder wieder an., Einen ganzen Bereich auf einmal an- oder abwählen., Alle Abwahlen aufheben - vom Zurücksetzen des Fortschritts bewusst getrennt:…, Atomar schreiben (erst temporär, dann ersetzen) - dasselbe Vorgehen wie in… (+19 more)

### Community 20 - "test_addon_analysis_sync.py"
Cohesion: 0.07
Nodes (35): apply_addon_progress(), parse_addon_progress(), Academy-Fortschritt, wie ihn das Addon zurückmeldet. Bewusst ein eigenes Modul…, {Charakter: (erledigt, abgewählt)}. Unvollständige Blöcke werden übersprungen…, Übernimmt den gemeldeten Stand in den AcademyService und speichert, wenn sich…, AddonAnalysisSync, Den Merker verwerfen, damit die nächste Zustellung auch dann schreibt, wenn…, Sofort zustellen, statt auf den Sync-Takt zu warten. Wird aus der Oberfläche… (+27 more)

### Community 21 - "AnalysisView"
Cohesion: 0.06
Nodes (32): AnalysisView, _format_amount(), QWidget, ANALYSE - die Tiefenauswertung des Pulls, den man vor sich hat. Die zweite der…, Die Tiefenauswertung. Eine Ansicht, kein Ort., Wessen Cooldowns der Zeitstrahl zeigt. Der Filter entscheidet; ohne Filter der…, Den Zeitstrahl für **einen** Spieler füllen. Für welchen, entscheidet derselbe…, Die Spielerliste des Filters mitziehen, ohne die laufende Auswahl zu verwerfen.… (+24 more)

### Community 22 - "analyzer/models.py"
Cohesion: 0.05
Nodes (41): Raidlog Analyzer - die Auswertungsschicht des Weint-Ökosystems. Dieses Paket…, AbilityDamage, ActivityEntry, CooldownState, DamageTakenEntry, EncounterInfo, MovementEntry, PullSummary (+33 more)

### Community 23 - "warcraftlogs_payload.py"
Cohesion: 0.09
Nodes (58): _battle_res_charges(), build_activity(), build_actor(), build_consumables(), build_cooldown_usage(), build_cooldowns(), build_damage_taken(), build_deaths() (+50 more)

### Community 24 - "preparation.py"
Cohesion: 0.05
Nodes (40): Wie weit ein Charakter vorbereitet ist, als Anteil von 0 bis 1. Gezählt wird,…, readiness(), build_page_specs(), PageId, PageSpec, Die Seitenregistrierung der Anwendung. Vorher war die Navigation an drei…, Beschreibung einer Seite. `icon_factory` und `page_factory` sind bewusst…, Die vollständige Seitenliste, in Navigationsreihenfolge. (+32 more)

### Community 25 - "test_theme_connections.py"
Cohesion: 0.05
Nodes (34): gc, HistoryCard, LegendEntry, QWidget, Die Lernkurve eines Charakters über seine letzten Pulls., Ein Eintrag der Legende: farbiger Strich, Beschriftung, Werte. Der Strich liest…, ProgressionChart, QWidget (+26 more)

### Community 26 - "test_raid_context.py"
Cohesion: 0.08
Nodes (49): Neutraler Snapshot für "noch keine Daten" - so kann die Oberfläche vom ersten…, context_from(), facts_line(), mode_label(), Der Kontext, wie er sich aus dem Dienst ergibt. Gelesen wird ausschliesslich…, "Pull 17 · Wipe · 42 % · 06:31" - jeder Teil fällt einzeln weg, wenn er fehlt.…, Wie der Kampf gerade gelesen wird - als Chip neben dem Bossnamen. Er…, Ob zwei Kontexte denselben Pull meinen. Gefragt wird über die Archivkennung,… (+41 more)

### Community 27 - "snapshot_from_payload"
Cohesion: 0.07
Nodes (57): Baut aus der Bot-Antwort das vollständige Bild eines Zeitpunkts. `age_seconds`…, Kurze Beschreibung des Berichts für die Statuszeile, z. B. "Thron des Donners ·…, report_label(), snapshot_from_payload(), Additiv wie alle v2-Felder: eine Antwort ohne `buffs` ist kein Fehler, sondern…, test_the_bot_payload_carries_the_block(), _deep_payload(), _payload() (+49 more)

### Community 28 - "test_access_profile.py"
Cohesion: 0.06
Nodes (56): build_profile_payload(), features_for(), label_for(), normalize_role(), Zuordnung Discord-Rolle -> Rang -> Freigaben. Diese Tabelle ist die Companion-…, Bestimmt aus den Discord-Rollennamen den Rang. Gibt (tier, matched_roles)…, Vollstaendige Freigabetabelle als {Schluessel: bool}. Bewusst vollstaendig und…, Baut die access_profile-Nutzlast aus der Bot-Antwort. Gibt (payload,… (+48 more)

### Community 29 - "Paths"
Cohesion: 0.06
Nodes (35): Ist dieser Ordner die gesuchte Installation?, WoWFinder, Config, Schreibt zuerst in eine temporäre Datei im selben Verzeichnis und ersetzt…, Die Kennung der aktiven Spielversion - **aufgelöst**, nie roh aus der Datei.…, Die aktive Spielversion als Eintrag aus `core/wow_clients.py`. Eine unbekannte…, Wechselt die Spielversion. Nimmt dabei die Mindeststufe mit, **falls sie nie…, Der hinterlegte Ordner einer Spielversion, oder None - auch dann, wenn er zwar… (+27 more)

### Community 30 - "CompanionManager"
Cohesion: 0.06
Nodes (13): BattleNetLauncher, _AutoSyncStarter, CompanionManager, QObject, Der Hintergrundwache sagen, dass ihre beiden Endpunkte gerade abgefragt wurden…, Prüft erneut gegen GitHub, ob ein Addon- oder Companion-Update verfügbar ist -…, Stößt start_auto_sync() garantiert im Hauptthread an, egal von welchem Thread…, `quiet` ist der Modus der Hintergrundwache (siehe core/update_watch.py):… (+5 more)

### Community 31 - "test_raid_center.py"
Cohesion: 0.06
Nodes (49): RaidLink, Ein Tiefenverweis auf einen Pull - "zeig mir *das* dort". Jedes Feld ist ein…, parametrize, Das Raid Center: ein Pull, vier Perspektiven. Diese Datei baut Widgets - wie…, Dieselbe Überlegung wie bei `MainWindow._ensure_page()`: alle vier im Voraus zu…, Der Kern des Umbaus. Der Kopfblock steht ausserhalb des Stapels; ein Wechsel…, Die Lernansicht baut je Bild ein vollständiges Profil und einen Trainingsplan,…, Der Dienst veröffentlicht weiter, während eine andere Seite im Vordergrund ist… (+41 more)

### Community 32 - "FightSummary"
Cohesion: 0.08
Nodes (32): FightSummary, Ein Eintrag der Report-Liste - genug, um ihn in einem Dropdown anzuzeigen, ohne…, Ein Eintrag der Pull-Liste innerhalb eines Reports., Kampfdauer als mm:ss., Ausgang des Pulls in einem Wort bzw. dem Restanteil des Bosses., Schwierigkeit, ersatzweise die Raidgroesse. Der Name der Schwierigkeit traegt…, ReportSummary, LastPullSync (+24 more)

### Community 33 - "test_discord_links.py"
Cohesion: 0.06
Nodes (50): channel_url(), feedback_url(), guild_url(), Der Link auf eine Discord-Gilde. Ohne Angabe die Gilde des Projekts., Der Link auf einen Kanal - und, wenn bekannt, auf eine bestimmte Nachricht…, Wohin der Knopf "Aufstellung im Discord" führt. Rein und ohne Qt - aus…, roster_target(), linux() (+42 more)

### Community 34 - "LoadingCard"
Cohesion: 0.07
Nodes (32): clock(), CooldownTimeline, QColor, QPainter, QWidget, Den ganzen Strahl auf einmal setzen. Auf einmal und nicht Zeile für Zeile: die…, Anfang, Mitte, Ende - drei Marken reichen. Eine vollständige Achsenbeschriftung…, Sekunden als MM:SS. Dieselbe Schreibweise wie überall sonst in WeintTV. (+24 more)

### Community 35 - "test_greeting.py"
Cohesion: 0.09
Nodes (48): daypart(), days_until(), greeting(), headline(), _local(), _now(), datetime, raid_phrase() (+40 more)

### Community 36 - "DiscordAccountStore"
Cohesion: 0.05
Nodes (32): DiscordAccountError, DiscordAccountStore, _log(), Exception, Speichert die verknüpfte Discord-Identität rein lokal auf dem Rechner des…, Legt die Verknüpfung ab. Wirft `DiscordAccountError`, wenn die Daten…, Meldet, dass der Bot das Companion-Token abgelehnt hat. Gibt `True` zurück,…, Die Verknüpfung liess sich nicht ablegen (unbrauchbare Daten oder ein… (+24 more)

### Community 37 - "RaidSnapshot"
Cohesion: 0.08
Nodes (35): RaidSnapshot, Mittlerer Laufweg des Raids. Eine Eigenschaft und kein Feld, damit der Schnitt…, Alle bekannten Spieler des Snapshots. Die Spezialisierung hängt am `Actor` und…, Alle bekannten Spielernamen des Snapshots, sortiert., Ein vollständiges, in sich konsistentes Bild eines Zeitpunkts. Die Oberfläche…, Ob überhaupt ein Raid erkannt wurde. Unterscheidet "verbunden, aber gerade…, Pull-Zeit als MM:SS - die Formatierung gehört hierher und nicht in jedes…, Ob überhaupt Tiefenauswertung vorliegt. Der einzige Schalter, den die… (+27 more)

### Community 38 - "test_academy_history_card.py"
Cohesion: 0.07
Nodes (37): Jeden beendeten Pull für die Lernkurve der Academy anbieten. Hängt am…, Der Zusatz unter der Kurve, wenn die Datenquelle ihn braucht. Bei der…, _source_note(), _Academy, _app(), _ArchiveState, _card(), _Config (+29 more)

### Community 39 - "test_last_pull.py"
Cohesion: 0.08
Nodes (46): from_fights(), from_history(), LastPull, parse_last_pull(), _parse_moment(), datetime, Der zuletzt gespielte Pull - lesen, rechnen, beschriften. **Warum es diese…, Die Kurve: geschaffter Anteil je Pull, ältester zuerst. Gezeichnet wird `100 -… (+38 more)

### Community 40 - "OverviewPage"
Cohesion: 0.06
Nodes (18): OverviewPage, WoW über Battle.net starten - derselbe Weg wie bis 1.7. `manager.start_wow()`…, Die Aufstellung dort öffnen, wo sie tatsächlich steht. Diese Karte kann den…, Über `core.browser.open_url()` - und nicht mehr über ein blankes…, Duck-getypt vom MainWindow gesetzt (`_ensure_page`). **Ein** Läufer für die…, Der zuletzt bekannte Raidtermin. Über `getattr`, weil `refresh()` auch aus…, Nur den Chip - läuft einmal pro Minute., Der Minutentakt: Countdown und Begrüßung. Beides hängt allein an der Uhr und… (+10 more)

### Community 41 - "test_analysis_guide.py"
Cohesion: 0.05
Nodes (36): _app(), context_header(), __init__(), _load_a_pull(), _Logger, fixture, Der Wegweiser durch die vier Ansichten des Raid Centers. Gemeldet wurde: "Viele…, `font()` faellt bei einem unbekannten Namen stumm auf `body` zurueck. Genau das… (+28 more)

### Community 42 - "UptimeEntry"
Cohesion: 0.09
Nodes (43): analyzer_analysis, _actors(), _apply_cooldowns(), apply_spec_reference(), _apply_uptimes(), _display_name(), _match(), Gemeldete Wirkungsdauern und Cooldowns gegen die Spezialisierung halten. Die… (+35 more)

### Community 43 - "CharacterLinksPage"
Cohesion: 0.07
Nodes (19): CharacterLinksClient, Den Stand zu **einem** Raid holen. `raid_id` wählt bei mehreren gleichzeitig…, Overview, Was der Bot zur Charakterzuordnung zu sagen hat., CharacterLinksPage, _class_items(), _default_class(), QWidget (+11 more)

### Community 44 - "LogWidget"
Cohesion: 0.06
Nodes (16): LogEntry, ConnectionsPage, Nur zeichnen. Hier stand ein `self.manager.full_refresh()` - ein vollständiger…, Der Config-Key heißt weiterhin "roster_sync_enabled" (siehe…, Stellt die zuletzt ausgewertete Analyse ins Addon, damit WeintTV und die…, Alles neu prüfen und dann synchronisieren. In einem eigenen kurzlebigen Thread…, LogsPage, QWidget (+8 more)

### Community 45 - "OverlayWindow"
Cohesion: 0.06
Nodes (21): _HealthBar, OverlayWindow, QWidget, Vom Datendienst abmelden, falls angemeldet. Mehrfach aufrufbar: `close()` löst…, _Academy, _app(), _Config, _Logger (+13 more)

### Community 46 - "test_addon_inbox.py"
Cohesion: 0.08
Nodes (31): AddonInbox, Die gemeinsame Zustellung Richtung Addon. InboxWriter.send_batch() ersetzt die…, Einen Kanal leeren, ohne die übrigen anzutasten., Ersetzt den Inhalt eines Kanals und schreibt die Inbox neu. Gibt True zurück,…, InboxWriter, Gegenrichtung zu SyncReader: schreibt Nachrichten von Companion Richtung Addon…, _inbox_body(), _Logger (+23 more)

### Community 47 - "test_character_report_sync.py"
Cohesion: 0.07
Nodes (31): apply_character_report(), parse_character_report(), Wer spielt gerade? - die Meldung des Addons. Bis WeintCodex 1.3.2.3 erfuhr die…, Zerlegt die Nutzlast. `None` heißt "unbrauchbar" - ohne Namen ist die Meldung…, Die Meldung an den `AcademyService` weiterreichen. Gibt die zerlegte Meldung…, academy(), _Config, _Logger (+23 more)

### Community 48 - "raid_schedule.py"
Cohesion: 0.06
Nodes (41): count_text(), normalize_own_state(), normalize_role(), own_signup_label(), own_signup_text(), own_signup_variant(), _parse_composition(), _parse_raid_id() (+33 more)

### Community 49 - "test_update_banner.py"
Cohesion: 0.05
Nodes (19): QObject, Die Anwendung selbst aktualisieren. Im Hintergrund-Thread, weil hier ein…, Beide Update-Kanäle, einmal. `finished` trägt die Komponente, den Erfolg und…, Addon installieren oder aktualisieren. Bewusst blockierend im Hauptthread, wie…, UpdateRunner, _app(), _Logger, _Manager (+11 more)

### Community 50 - "NavColumn"
Cohesion: 0.08
Nodes (11): _AccountButton, NavColumn, done(), NavItem, QFrame, Die Oberkante des Balkens, sodass er auf der Höhe des Eintrags zentriert steht., Die Wahl des Nutzers umschalten., Von außen erzwungenes Einklappen (Haltepunkt, WeintTV). Die Wahl des Nutzers… (+3 more)

### Community 51 - "Card"
Cohesion: 0.06
Nodes (17): CharacterCard, Eine Karte je Charakter: Name in Klassenfarbe, Spezialisierung, Stufe,…, QVBoxLayout, FocusCard, Die Karte um die Baustellen - samt Leerzustand., QWidget, RatingGrid, RatingTile (+9 more)

### Community 52 - "test_roster_card.py"
Cohesion: 0.09
Nodes (36): Der nächste Raid: Termin, Titel, **Aufstellung**. **Was sich hier geändert…, `schedule` ist ein `RaidSchedule`, `days` seine noch bevorstehenden Termine…, So viele Bloecke, wie Termine anstehen - fehlende werden angelegt,…, RosterCard, _app(), _card(), _Config, _own_states() (+28 more)

### Community 53 - "RaidCenterPage"
Cohesion: 0.07
Nodes (21): _create_view(), QHBoxLayout, QWidget, RaidCenterPage, Die vier Perspektiven, ein Erklärsatz, und die zwei Werkzeuge, die nirgends…, Die Ansicht zu `key` - gebaut, falls sie noch ein Platzhalter ist. Dieselbe…, Die Tiefenverweise einer Ansicht anschliessen - duck-getypt, genau wie…, Die Perspektive wechseln - **ohne** den Kontext anzutasten. Das ist die eine… (+13 more)

### Community 54 - "test_academy_selection.py"
Cohesion: 0.07
Nodes (29): _Config, _Logger, _Manager, fixture, _RaidData, Wer ist "ich"? - die Charakterauswahl der Academy. Diese Datei hält die Regeln…, Bis 1.6.2 kam hier der alphabetisch erste Raider heraus - bei jedem Snapshot…, Sonst stünde eine Auswahl da, zu der es keine Daten gibt. (+21 more)

### Community 55 - "test_lesson_catalog.py"
Cohesion: 0.08
Nodes (36): all_lessons(), lessons_for_actor(), lessons_in_category(), Alle für einen Spieler in Frage kommenden Lektionen, Spezielles zuerst. Ohne…, Die Lektionen eines Bereichs, in derselben Reihenfolge., Der vollständige Katalog - für Übersichten und für die Prüfung auf eindeutige…, specs_for_role(), _actor() (+28 more)

### Community 56 - "test_changelog.py"
Cohesion: 0.08
Nodes (38): format_changelog_body(), flush(), Wandelt die Markdown-Syntax aus CHANGELOG.md in lesbare Absätze mit…, Dasselbe wie `_split_sections()`, nur mit dem Datum aus der Überschrift - die…, split_entries(), strip_markdown(), addon_entries(), Der Text, der über dem Update-Knopf steht. `version` ist die Fassung, die er… (+30 more)

### Community 57 - "classes/_common.py"
Cohesion: 0.06
Nodes (28): analyzer_academy_lessons_classes, buff_uptime_check(), cooldown_check(), defensive_check(), dispel_check(), hot_uptime_check(), interrupt_check(), Gemeinsame Importe der Klassendateien. Jede Klassendatei braucht dieselbe… (+20 more)

### Community 58 - "test_discord_app.py"
Cohesion: 0.10
Nodes (36): find_launcher(), Der vollständige Aufruf, mit dem die Discord-Anwendung diese Adresse öffnet -…, _Answer, applications(), _entry(), _handler(), linux(), fixture (+28 more)

### Community 59 - "MainWindow"
Cohesion: 0.09
Nodes (9): Edges, MainWindow, Einen Spieler in der Lernansicht öffnen. Seit 4.0 ist das kein Seitenwechsel…, Das Raid Center öffnen und dort einen Tiefenverweis auflösen. Die Reihenfolge…, Hintergrunddienste beim Beenden geordnet stoppen. Der RaidDataThread ist zwar…, Die Seite zu `page_id` - gebaut, falls sie noch ein Platzhalter ist. Alles, was…, Ob diese Seite die Navigationsspalte einklappt. Zwei Gründe können das…, motion.page: Deckkraft 0 -> 1 und ein Versatz von 12 px in Navigationsrichtung,… (+1 more)

### Community 60 - "test_live_bridge.py"
Cohesion: 0.09
Nodes (29): Die aktuelle Vereinigung erneut hinausschreiben, ohne dass ein Absender etwas…, LiveBridgeWriter, _bridge(), _Logger, _Manager, fixture, skipif, Die Zustellung, die ein /reload überlebt. Der Weg über WeintCompanionInboxDB… (+21 more)

### Community 61 - "test_academy_checks.py"
Cohesion: 0.13
Nodes (36): evaluate_check(), evaluate_lesson(), metric_names(), _moment(), Alle auflösbaren Kennzahlen. Der Katalogtest hängt daran: ein Tippfehler in…, Der Wert einer Kennzahl, oder None wenn sie sich nicht bestimmen lässt. Wirft…, Der Zeitpunkt, an dem sich ein gescheitertes Kriterium festmacht - das…, Das Gesamturteil zu einer Lektion. Kombinationsregel: ein gescheitertes… (+28 more)

### Community 62 - "academy/models.py"
Cohesion: 0.09
Nodes (22): Die Lernlogik der WeintAcademy. Sie liegt bewusst im Analyzer und nicht in der…, _no_hits(), Bossbezogene Lektionen. Die Ebene, auf der aus "vermeidbarer Schaden" konkreter…, "Keine vermeidbaren Treffer" - das mit Abstand häufigste Kriterium…, Allgemeine Lektionen - gültig für jede Klasse und jede Rolle. Sie sind die…, Der Lektionskatalog der WeintAcademy. Aus einer Datei ist ein Paket geworden,…, _all_lessons(), _build_index() (+14 more)

### Community 63 - "Resources"
Cohesion: 0.10
Nodes (10): Path, Gibt den Projektordner zurück. Entwicklung: Projektordner/ PyInstaller:…, Das tatsächliche Discord-Logo (Clyde-Mark) - anders als Resources.discord()…, Das Ökosystem-Artwork - Startbildschirm und Einstellungen → Über zeigen…, Resources, QVBoxLayout, Erklärt, warum die Tiefenauswertung leer ist - statt sie als Reihe leerer…, install_fonts() (+2 more)

### Community 64 - "StatusDot"
Cohesion: 0.08
Nodes (15): _Endpoint, QHBoxLayout, Ein Ende der Flusskarte: Symbol, Name, Zustandszeile mit `StatusDot`.…, BridgeRow, BridgeTile, QWidget, Drei Brücken und der Zeitpunkt des letzten Abgleichs., `state` ist der `AppState` des CompanionManagers. Bewusst **kein** eigener… (+7 more)

### Community 65 - "RosterStrip"
Cohesion: 0.09
Nodes (30): QWidget, Die Reihen setzen. Gleicher Inhalt heißt kein Neuzeichnen - die Übersicht ruft…, Kästchenbreite, Abstände und die Breite je Reihe. Eine Reihe ist nie schmaler…, Eine Rolle: Beschriftung, gefüllte Plätze, offene Plätze. `filled` trägt je…, RosterStrip, SlotGroup, QFontMetricsF, Ein zugesagter Platz ohne gemeldete Klasse trägt die Akzentfarbe. Gelesen wird… (+22 more)

### Community 66 - "player_abilities.py"
Cohesion: 0.09
Nodes (34): aliases_of(), _all_names(), _build_canonical(), _build_groups(), canonical(), _key(), known_abilities(), matches() (+26 more)

### Community 67 - "test_quick_actions.py"
Cohesion: 0.08
Nodes (21): _Config, _launch(), _Logger, _Manager, _Page, Die beiden Schnellzugriffe, die der 2.0-Umbau verloren hat. Bis 1.7 sass auf…, Der Kern der Regression: der Knopf muss den Battle.net-Starter erreichen.…, Mit hinterlegtem Startbefehl gilt unter Linux dasselbe. (+13 more)

### Community 68 - "test_loading_progress.py"
Cohesion: 0.08
Nodes (33): blend(), _clock(), estimate(), overdue(), progress_text(), Wie lange ein Abruf noch dauert - und wie man das sagt, ohne etwas zu…, Eine frische Messung anhängen und die Liste kurz halten. Unsinnige Werte…, Wie voll der Balken steht, 0.0 - 1.0 (ausschliesslich). Bis zur Schätzung läuft… (+25 more)

### Community 69 - "checks.py"
Cohesion: 0.08
Nodes (22): _buff_uptime(), _compare(), _cooldown_alignment(), _cooldown_usage(), _cooldown_wasted(), _cooldowns(), _damage_rank_ratio(), _dot_uptime() (+14 more)

### Community 70 - "test_academy_service.py"
Cohesion: 0.09
Nodes (24): analyzer_academy_lessons, _Config, _Logger, _Manager, _profile(), Fortschritt und Lektionsauswahl der Academy auf der Platte. Der Kernpunkt:…, Der eigentliche Grund für die Speicherung von Ausschlüssen: eine Lektion, die…, Sonst könnte die Fortschrittsanzeige nie 100 Prozent erreichen: der Nenner… (+16 more)

### Community 71 - "test_names.py"
Cohesion: 0.09
Nodes (31): names_equal(), normalize_name(), Charakternamen vergleichen. Derselbe Spieler heißt je nach Quelle anders…, "Name-Realm" -> ("Name", "Realm"). Ohne Bindestrich bleibt der Realm leer.…, Vergleichsform der Basis (ohne Realm, casefold). Nur für Vergleiche und…, Derselbe Charakter? Der Realm zählt nur mit, wenn ihn **beide** Seiten…, split_name(), Charakternamen vergleichen. Die drei Regeln aus `analyzer/names.py` stehen hier… (+23 more)

### Community 72 - "GitHubUpdater"
Cohesion: 0.09
Nodes (20): GitHubRelease, GitHubUpdater, Sucht in "assets" nach einer zu "asset_name" gehörenden "<name>.sha256"-Datei…, Die nächste Abfrage geht wieder wirklich zu GitHub. Der Zwischenspeicher hält…, Liefert die Commit-Titel, die im Release "tag_name" enthalten sind - verglichen…, Ob "name" eine von der CI veröffentlichte "<asset>.sha256"- Prüfsummendatei…, FakeClient, FakeResponse (+12 more)

### Community 73 - "test_net_errors.py"
Cohesion: 0.11
Nodes (31): bot_unreachable_text(), _chain(), is_dns_failure(), is_timeout(), Warum der Bot nicht erreichbar ist - in einem Satz, der den nächsten Schritt…, Der Satz, der dem Nutzer statt der Systemmeldung angezeigt wird. `address` ist…, Die Ausnahme und alles, was sie ausgelöst hat. Mit Abbruch nach zehn Gliedern…, Heißt diese Ausnahme "den Namen gibt es nicht"? (+23 more)

### Community 74 - "test_archive_browser.py"
Cohesion: 0.12
Nodes (32): _browser(), _flat(), _loaded(), Der Archivbrowser und die Quellenansicht des Raid Centers. Diese Datei baut…, Die Zeilen einer Spalte als Textlisten., Der Browser - seit 4.0 ausschliesslich als Teil der Quellenansicht., Ob der Browser einen geladenen Pull gemeldet hat. Das ist der Nachfolger von…, Das Datum steht links am Abend; zwanzig Mal zu wiederholen wäre Lärm -… (+24 more)

### Community 75 - "test_raid_schedule_special.py"
Cohesion: 0.09
Nodes (24): day_text(), "Mittwoch, 12.08. um 20:00" - die Zeile unter dem Titel., _both(), _Logger, _moment(), datetime, Der Sonderraid in der Raidübersicht - dieselbe Strecke wie ein normaler Raid.…, `next_day()` ist die eine Stelle, aus der Kopfzeile und Countdown lesen. Sie… (+16 more)

### Community 76 - "test_academy_empty_state.py"
Cohesion: 0.09
Nodes (30): academy_empty_action(), academy_empty_text(), Warum die Academy gerade nichts zu zeigen hat. Leerer Text heißt: es gibt einen…, Welcher Weg aus dem Leerzustand führt. Nur im Fall "kein Raid erkannt" gibt es…, Was die Academy sagt, wenn sie nichts zu sagen hat - und was sie sagt, wenn sie…, Den laufenden Bossanteil als Wipe auszugeben wäre eine Behauptung über einen…, Die fehlende Liste ist der Punkt: sie beantwortet als einzige Zahl dieser Seite…, Ein Strich heisst "nicht geliefert", eine Null wäre ein Vorwurf. (+22 more)

### Community 77 - "test_appearance_section.py"
Cohesion: 0.09
Nodes (27): _app(), _click(), _Config, _Manager, _marked(), fixture, parametrize, Einstellungen -> Erscheinungsbild: die drei Wahlmöglichkeiten. Der… (+19 more)

### Community 78 - "test_overview_header.py"
Cohesion: 0.08
Nodes (16): _app(), _Logger, _Manager, page(), _pump(), fixture, Der Kopf der Übersicht: Begrüßung und "Erneut prüfen". Zwei Dinge werden hier…, Der angemeldete Charakter ist die einzige Antwort auf "wer bin ich", die… (+8 more)

### Community 79 - "Runtime"
Cohesion: 0.11
Nodes (23): contextlib, open_app_link(), open_url(), Eine Adresse im System-Browser öffnen - an genau einer Stelle. **Warum eine…, Öffnet `url` im System-Browser. `logger` ist der `Logger` der App (oder `None`…, Öffnet eine Adresse mit eigenem Schema (`discord://…`) in der zuständigen…, _launch(), open_link() (+15 more)

### Community 80 - "parse_character_sheet"
Cohesion: 0.09
Nodes (30): _at(), _counts(), _float(), _int(), open_slots(), parse_character_sheet(), Der Ausrüstungsstand eines Charakters - die Meldung des Addons. Bis 2.0.0…, Ein unbekannter Status wird durchgereicht, nicht ersetzt. Eine künftige Addon-… (+22 more)

### Community 81 - "test_discord_auth.py"
Cohesion: 0.10
Nodes (21): DiscordAuthError, parse_exchange_response(), Exception, Führt den kompletten OAuth-Login aus: startet einen temporären lokalen HTTP-…, Prüft die Antwort des Bots auf den Code-Austausch, bevor sie abgelegt wird.…, _browser_der_sofort_zurueckkommt(), _port_frei(), _Protokoll (+13 more)

### Community 82 - "AddonPage"
Cohesion: 0.08
Nodes (11): Die Ansicht öffnen - der eine Einstiegspunkt für alle Aufrufer., show_changelog(), AddonPage, Über den gemeinsamen `UpdateRunner`. Der Ablauf selbst (Karte auf „lädt",…, Duck-getypt vom MainWindow gesetzt (`_ensure_page`)., Links steht, wer Handlungsbedarf hat (§6.4). Bei keinem oder beiden bleibt das…, Page, PageHeader (+3 more)

### Community 83 - "discord_app.py"
Cohesion: 0.11
Nodes (29): _appimage_dirs(), _data_dirs(), desktop_file(), exec_line(), _executable(), _expand(), _from_appimage(), _from_desktop_entries() (+21 more)

### Community 84 - "RaidContext"
Cohesion: 0.09
Nodes (25): boss_line(), empty_hint(), empty_line(), instance_line(), outcome_label(), RaidContext, Der Kampf, den der Nutzer gerade vor sich hat - so weit bekannt. `known` ist…, Ob etwas anderes als der Live-Feed gezeigt wird - dieselbe Frage wie… (+17 more)

### Community 85 - "FakeService"
Cohesion: 0.09
Nodes (17): FakeService, QObject, Ein Kill schlägt jeden Wipe - `best_try()` entscheidet das, und dieser Knopf…, *lock, don't hide*: ein Knopf, der je nach Lage verschwindet, lässt sich weder…, `SegmentedControl.setValue()` tut bei einem unbekannten Wert stillschweigend…, Nur das, was der Browser wirklich anspricht., _source_view(), test_a_quick_button_without_a_target_is_disabled_not_hidden() (+9 more)

### Community 86 - "PullRecord"
Cohesion: 0.08
Nodes (15): from_dict(), PullRecord, Ein aufgezeichneter Pull - so viel, wie die Kurve braucht, und keine Zeile…, Die Sterne eines Bereichs - 0 heisst **nicht bewertet**., Das Mittel über die bewerteten Bereiche. Unbewertete Bereiche zählen nicht mit,…, "Malkorok · Pull 3" - die Beschriftung eines Punktes., Einen Datensatz einlesen - `None`, wenn er unbrauchbar ist. Defensiv wie…, AcademyHistory (+7 more)

### Community 87 - "test_warcraftlogs_provider.py"
Cohesion: 0.15
Nodes (25): analyzer_providers, FakeFetch, Der WarcraftLogs-Provider ist die einzige Quelle mit eigenem Hintergrund-…, Startet den Provider und stellt sicher, dass er am Ende des Tests wieder…, Der Service fragt im Sekundentakt, WarcraftLogs liefert aber nur alle paar…, Würde die Ausnahme den Thread beenden, bliebe die Quelle nach einer einzigen…, Ein einzelner erfolgloser Abruf (Bot kurz nicht erreichbar) darf den zuletzt…, Nach einem beendeten Raid soll WeintTV nicht stundenlang denselben… (+17 more)

### Community 88 - "test_backup_saved_variables.py"
Cohesion: 0.10
Nodes (27): Sichert den Addon-Ordner und - sofern `wow_path` bekannt ist - die…, Alle `WeintCodex.lua` unter `WTF/Account/*/SavedVariables/`. Bewusst **alle**…, Die Spielstand-Einträge eines Archivs (leer bei einem Backup aus einer Fassung…, saved_variable_files(), saved_variable_members(), _addon(), manager(), fixture (+19 more)

### Community 89 - "LearnView"
Cohesion: 0.10
Nodes (13): LearnView, QWidget, Das Coaching zu diesem Pull. Eine Ansicht, kein Ort., Die Karte über der Seite: was fehlt, und was dagegen hilft. Formuliert wird…, Die Lernkurve zeichnen - die aufgezeichneten Pulls dieses Charakters, nicht der…, Der Satz zur Übungsserie am Trainingsdummy - leer, wenn für diese…, Die Spaltenzahl des Bewertungsrasters (§6.3): sechs bei voller Breite, drei…, Die Kennzahlkacheln neu anordnen. Die Kacheln werden dabei **umgehängt und… (+5 more)

### Community 90 - "SetupWizard"
Cohesion: 0.12
Nodes (8): _DiscordLoginBridge, QDialog, QObject, QWidget, Für Schritte ohne "gefunden/fehlt"-Zustand (Schritt 4: Aussehen wählen hat…, Gerüst eines Schritts: Rubrik, Titel, Erklärung, Statuszeile, ein Hauptknopf., SetupWizard, _Step

### Community 91 - "test_damage_analysis.py"
Cohesion: 0.18
Nodes (26): build_damage_taken(), classify_abilities(), derive_mechanics(), merge_mechanics(), Die Schadenszeile eines Spielers samt Aufteilung in vermeidbar / unvermeidbar /…, Aus vermeidbaren Treffern werden Mechanikfehler. Das ist die Brücke, über die…, Führt die vom Bot gelieferten und die hier abgeleiteten Mechanikfehler…, Reiht rohe `(ability, amount, hits, source_name)`-Zeilen zu eingeordneten… (+18 more)

### Community 92 - "test_discord_section.py"
Cohesion: 0.12
Nodes (22): resolve_bot_base_url(), Ein Modulimport darf keine Verzeichnisse im Benutzerprofil erzeugen, nur weil…, test_das_lesen_legt_kein_verzeichnis_an(), _abschnitt(), _app(), _Konten, _Manager, _Protokoll (+14 more)

### Community 93 - "test_tokens.py"
Cohesion: 0.09
Nodes (21): build_stylesheet(), Das globale Stylesheet fuer den uebergebenen Themezustand., mix(), "#RRGGBB" -> (r, g, b)., Eine Farbe mit Deckkraft, als `rgba(...)` für Qt-Stylesheets. Die eine Stelle,…, Zwei Farben mischen, `amount` ist der Anteil von `foreground`. Gebraucht, wo…, rgb(), tint() (+13 more)

### Community 94 - "TitleBar"
Cohesion: 0.11
Nodes (9): QFrame, QLabel, Markenplakette, Produktname, Version - und rechts die drei Knöpfe., Senkrechter Verlauf plus 1-px-Unterkante (§4). Gemalt und nicht per Stylesheet…, Ob an dieser Stelle gezogen werden darf. Die Knöpfe sind ausgenommen - ein Zug,…, Überlässt das Ziehen dem Fenstermanager statt es selbst per `move()`…, Einer der drei Fensterknöpfe (28 x 24 px). Als QLabel statt QPushButton, damit…, TitleBar (+1 more)

### Community 95 - "test_academy_dummy_sync.py"
Cohesion: 0.21
Nodes (25): apply_dummy_practice_session(), parse_dummy_practice_session(), Übernimmt eine gemeldete Sitzung in den AcademyService und speichert, wenn sich…, Eine einzelne Sitzung aus der Pipe-Zeichenkette, oder None bei einem…, _Manager, _payload(), Rotationstrainer-Sitzungen vom Addon -> Streak -> Trainingsplan. Der Kernpunkt:…, Wer die alte Fassung benutzt hat, hat beide Schreibweisen in der Datei. Beim… (+17 more)

### Community 96 - "storage_usage.py"
Cohesion: 0.11
Nodes (19): cleanup_text(), count_folder(), empty_report(), folder_hint(), folder_text(), FolderUsage, format_size(), Path (+11 more)

### Community 97 - "Rating"
Cohesion: 0.10
Nodes (11): FocusRow, QFrame, Die Höhe, die diese Zeile bei dieser Breite wirklich braucht. Über das eigene…, Eine Baustelle: Bereich, Sterne, Begründung, Lektion, zwei Wege., QSize, QWidget, Rating, Null Sterne heißt "keine Daten" - siehe Modulkommentar. (+3 more)

### Community 98 - "check_version.py"
Cohesion: 0.14
Nodes (23): re, changelog_has(), check(), installer_iss(), main(), normalize(), Prüft, ob ein Tag und die Versionsnummern im Repo zusammenpassen. Der Grund für…, "v1.2.4", "V1.2.4" und "1.2.4" sind dieselbe Version. (+15 more)

### Community 99 - "test_character_links_page.py"
Cohesion: 0.10
Nodes (14): _app(), _Config, _Logger, _Manager, page(), fetch(), fixture, Die Raidwahl auf der Seite "Charakterzuordnung". Gemeldet wurde: "Zur Zeit… (+6 more)

### Community 100 - "FakeService"
Cohesion: 0.08
Nodes (4): FakeService, QObject, Die Zeitleiste ist angekommen - der Schritt, auf den ein vorgemerkter Sprung…, Der Datendienst, so weit das Raid Center ihn anspricht. Er **hält den Zustand…

### Community 101 - "find_combat_log"
Cohesion: 0.13
Nodes (19): Zugriff auf das Combat-Log von World of Warcraft. Iteration 1 enthält hier…, CombatLogLocation, find_combat_log(), logs_directory(), Path, Findet die Combat-Log-Datei einer WoW-Installation. WoW schreibt das…, Ergebnis der Suche. `path` ist None, wenn nichts gefunden wurde; `reason`…, Das Logs-Verzeichnis einer Installation, oder None wenn der übergebene Pfad… (+11 more)

### Community 102 - "sync_manager.py"
Cohesion: 0.11
Nodes (15): CharacterSyncClient, Meldet die vom Addon bekannten Twinks (Name + Klasse) authentifiziert an den…, `wow_client` ist die Spielversion, aus der die Twinkliste stammt. Der Bot…, SyncManager, SyncClient, requests, _Antwort, gesendet() (+7 more)

### Community 103 - "test_character_links_raid_choice.py"
Cohesion: 0.12
Nodes (21): raid_choices(), RaidChoice, Ein wählbarer Raid: Kennung plus fertige Beschriftung. Die Beschriftung…, Was im Auswahlkasten steht. Der Titel trägt die Auskunft; Größe und Termin…, Alle gleichzeitig laufenden Raids als Auswahl, der nächste zuerst. **Wozu.**…, _client(), payload(), Tests fuer die Raidwahl der Charakterzuordnung. Der Fehler, den sie festhalten:… (+13 more)

### Community 104 - "test_storage_usage.py"
Cohesion: 0.15
Nodes (24): Die einzige Stelle dieser Datei, die die Platte anfasst. Die beiden Pfade…, scan(), _fill(), Wann sagt die Anwendung, dass sich Downloads und Backups anhäufen? Jede Addon-…, Dieselbe Zählweise, mit der *Einstellungen → Backups* seit jeher zählt und…, Eine Zahl allein sagt nicht, worum es geht: sechs Addon-Backups sind wenige…, Zwei Meldungen übereinander wären zweimal derselbe Weg zu demselben Knopf., Nichts da, nichts geändert - `process()` darf die sichtbare Seite nicht neu… (+16 more)

### Community 105 - "resolve"
Cohesion: 0.12
Nodes (23): _cross(), LayoutState, WeintCompanion 2.0 Haltepunkte Drei Schwellen entscheiden, wie sich das Fenster…, Was bei der aktuellen Fensterbreite gilt. Drei unabhaengige Aussagen statt…, Der Layoutzustand fuer diese Breite. `previous` ist der zuletzt geltende…, Ob die Schwelle bei dieser Breite greift, mit Hysterese. Aktiv wird sie…, resolve(), Die Haltepunkte entscheiden, was unter der Entwurfsgröße passiert. Der… (+15 more)

### Community 106 - "LiveView"
Cohesion: 0.10
Nodes (14): LiveView, QVBoxLayout, QWidget, Der laufende Kampf. Eine Ansicht, kein Ort - sie trägt keinen eigenen Kopf und…, BarTable, QWidget, Eine Rangliste mit Kopfzeile., _Entry (+6 more)

### Community 107 - "SplashScreen"
Cohesion: 0.14
Nodes (12): QPainter, QRectF, QSize, QWidget, Die Vorgabegröße, aber nie breiter als gut die Hälfte des Bildschirms - auf…, Die *sichtbare* Höhe des Bildes - die volle Höhe abzüglich des abgeschnittenen…, Die Höhe, auf die das Bild skaliert wird, bevor unten abgeschnitten wird. Die…, `value` von 0.0 bis 1.0. Wird geklemmt, damit ein Schritt zu viel den Balken… (+4 more)

### Community 108 - "init_theme"
Cohesion: 0.13
Nodes (21): init_theme(), Den ThemeManager mit der Konfiguration verbinden. Einmal beim Programmstart,…, _app(), _Config, _images_per_accent(), Folgen die akzenttragenden Bausteine einem Akzentwechsel? Der Entwurf lässt den…, Die Gegenprobe: der Zweitknopf ist bewusst neutral. Änderte auch er sich, wäre…, Jade ist heller als Bernstein und verlangt eine dunkle Schrift. Vorher stand… (+13 more)

### Community 109 - "ArchiveBrowser"
Cohesion: 0.17
Nodes (5): ArchiveBrowser, QVBoxLayout, QWidget, Zwei Spalten, ein Suchfeld, ein Schalter. **Kein eigener Kopf und kein…, Vor dem abschliessenden Stretch einfügen, damit die Zeilen oben bleiben.

### Community 110 - "quote_lua_string"
Cohesion: 0.15
Nodes (17): messages: Liste von {"type": ..., "payload": ...}. Ersetzt die komplette Inbox-…, Die Nachrichten einer Zustellung als Lua-Tabelleneinträge. Steht hier und nicht…, render_entries(), Die Zustellung, die ein /reload überlebt. Der übliche Weg Richtung Addon ist…, Schreibt die Zustellung, wenn sich ihr Inhalt gegenüber der Datei geändert hat.…, _lua_number(), matching_brace(), Path (+9 more)

### Community 111 - "test_archive_index.py"
Cohesion: 0.21
Nodes (23): group_fights(), Pulls nach Boss gebündelt, in der Reihenfolge seines ersten Auftretens im…, _fight(), _fights(), Der Archivbrowser entscheidet nichts über einen Kampf - er entscheidet, welche…, "garrosh kill" findet den Kill auf Garrosh, obwohl die beiden Wörter auf der…, Gesucht wird über das, was auf der Zeile steht - eine Suche über unsichtbare…, "00:00" wäre von einer echten Uhrzeit nicht zu unterscheiden, und ein Pull um… (+15 more)

### Community 112 - "test_backend_config.py"
Cohesion: 0.14
Nodes (23): Die abweichende Adresse ablegen - oder die Ablage räumen. Liefert die abgelegte…, write_bot_url_override(), _ablage(), _neu_laden(), Die Basis-URL des Bots - und warum sie sich überschreiben lässt. Der Bot liegt…, Der eingebaute Wert muss die Adresse sein, unter der der Bot tatsächlich läuft…, Das Modul mit gesetzter Umgebung neu einlesen - die Auflösung passiert beim…, `bot_url_override_path()` setzt den Pfad bewusst ohne `Paths.config()`… (+15 more)

### Community 113 - "CompanionUpdater"
Cohesion: 0.13
Nodes (12): CompanionUpdater, Ergebnis wird für die Laufzeit des Prozesses zwischen- gespeichert - VERSION…, Erkennt ein Update, das zuletzt nicht zu Ende lief (z. B. weil der Updater-…, Startet das Updater-Skript so, dass es das Beenden von WeintCompanion überlebt.…, Prüft, ob der aktuelle Prozess innerhalb einer transienten systemd-Scope läuft…, Prüft, ob eine funktionierende D-Bus-User-Session Umgebung vorhanden ist.…, Startet das Wartescript unsichtbar (kein Konsolenfenster) und komplett…, Läuft in einem Hintergrund-Thread (siehe… (+4 more)

### Community 114 - "_pull_snapshot"
Cohesion: 0.10
Nodes (16): _Logger, _Manager, _pull_snapshot(), Ein beendeter Pull, in dem der Spieler auch vorkommt - sonst entstünde ein…, Die Live-Quelle liefert denselben beendeten Kampf weiter aus - aus einem Pull…, `resolve_player_name()` rät nicht. Eine Kurve unter einem geratenen Namen wäre…, Ohne Kampfdaten entsteht ein leeres Profil. Ein Punkt daraus wäre eine Null, wo…, _service() (+8 more)

### Community 115 - "class_abilities.py"
Cohesion: 0.15
Nodes (21): aura_kind(), _buff(), _build_ability_index(), _build_aura_index(), _build_index(), _build_name_index(), _build_spec_lookup(), display_name() (+13 more)

### Community 116 - "specs.py"
Cohesion: 0.13
Nodes (21): _build_by_name(), _build_index(), find(), _key(), Die Spezialisierungen von *World of Warcraft: Forever* - deutsch, englisch und…, Vergleichsform eines Namens: kleingeschrieben und ohne alles, was nur…, Derselbe Bestand ohne Klasse - der Notweg für Antworten, die keine Klasse…, Die Spezialisierung zu Klasse und Bezeichnung, oder None. Ohne passende Klasse… (+13 more)

### Community 117 - "test_startup_popups.py"
Cohesion: 0.15
Nodes (22): AST, FunctionDef, Module, _app(), _calls(), _function(), Die App muss starten - auch beim ersten Start nach einem Update. Der Bericht:…, Ein einziges `processEvents()` bleibt nötig, damit der Startbildschirm… (+14 more)

### Community 118 - "PulseClock"
Cohesion: 0.12
Nodes (11): PulseClock, QObject, Einen sichtbaren Pulspunkt anmelden. Aufzurufen, wenn der Punkt sichtbar wird -…, Die Art, die gerade pulsen darf - oder None., Ob ein Punkt dieser Art gerade pulsen darf. Ein Warnpunkt, der nicht darf,…, Die Phase im Puls, 0.0 bis 1.0., Die Deckkraft eines Punktes dieser Art: 1.0 bis OPACITY_LOW und zurueck…, Die Skalierung eines Punktes dieser Art: 1.0 bis SCALE_LOW. (+3 more)

### Community 119 - "test_class_avatar.py"
Cohesion: 0.12
Nodes (17): ClassAvatar, QWidget, Eine quadratische Kachel mit dem Klassenwappen., _app(), _Config, _opaque_pixels(), Trägt jede Klasse ein Wappen - und wird es auch gezeichnet? Das Charakterbild…, Zwei Klassen dürfen nicht dasselbe Bild ergeben - sonst hätte sich irgendwo ein… (+9 more)

### Community 120 - "RaidDataProvider"
Cohesion: 0.10
Nodes (12): ABC, RaidDataProvider, Die Schnittstelle jeder Raid-Datenquelle. Der Vertrag ist absichtlich winzig -…, Optionale Zusatzinfo für die Oberfläche (erkannter Pfad, Grund für "keine…, Quelle aktivieren. Mehrfaches Aufrufen muss folgenlos sein., Quelle freigeben. Mehrfaches Aufrufen muss folgenlos sein., Aktuelles Gesamtbild. Wirft nie - siehe Modulkommentar., Kurzer Herkunftstext, z. B. "Simulation" oder "Combat-Log (WoWCombatLog.txt)". (+4 more)

### Community 121 - "changelog_source.py"
Cohesion: 0.16
Nodes (19): ChangelogEntry, CHANGELOG.md lesen - für das "Was ist neu"-Fenster, für die Änderungsansicht…, Eine CHANGELOG.md von der Platte, neueste Fassung zuerst. Eine fehlende oder…, Eine Fassung mit ihrem Datum und ihrem Text., read_entries(), flush(), companion_entries(), entries_for() (+11 more)

### Community 122 - "test_tour.py"
Cohesion: 0.13
Nodes (20): _build_tour_pages(), Eine Seite der Einführung. `icon` ist der Dateiname ohne Endung unter…, TourPage, _dialog(), _pages_with_a_scrollbar(), Die Einführung. Zwei Sorten Fehler werden hier abgefangen, und beide sind von…, Ein Schalter ohne Folgenangabe ist eine Frage ohne Antwort. Wer nicht weiss,…, Der Ausgang bleibt erreichbar. Er wird auf der letzten Seite ausgeblendet (dort… (+12 more)

### Community 123 - "test_task_card.py"
Cohesion: 0.12
Nodes (16): _app(), card(), _Config, fixture, Die Aufgabenkarte der Übersicht. Sie ist die Antwort auf die Frage, mit der…, Die Reihenfolge ist eine Eigenschaft der Karte und nicht der Seite, die sie…, Der Knopf ist das Aufnahmekriterium: gibt es keinen sinnvollen, gehört die…, `refresh()` läuft bei jeder Zustandsänderung. Würden die Zeilen dabei angehängt… (+8 more)

### Community 124 - "mock_schedule.py"
Cohesion: 0.14
Nodes (20): normalize_name(), Die Vergleichsform eines Fähigkeitsnamens - öffentlich, weil die Anreicherung…, _build_spec_cooldowns(), _build_spec_uptimes(), _casts_for(), cooldowns_for(), damage_taken_for(), _known_names() (+12 more)

### Community 125 - "archive_index.py"
Cohesion: 0.13
Nodes (20): day_label(), fight_count(), last_kill(), latest_report(), loading_text(), match_fight(), match_report(), _matches() (+12 more)

### Community 126 - "_snapshot"
Cohesion: 0.13
Nodes (17): pull_key(), qualifies(), Ob dieser Snapshot einen **beendeten, brauchbaren** Pull beschreibt. Drei…, Die Kennung, unter der ein Pull genau einmal aufgezeichnet wird. **Mit `origin`…, Der Charakter, für den das Profil gebaut wird - oder `""`. **Rät nicht.** Bis…, Einen **beendeten** Pull für die Lernkurve aufzeichnen. Gibt zurück, ob dabei…, Die Simulation liefert zwischen zwei Pulls ausdrücklich einen Snapshot ohne…, Zwölf Sekunden haben keine Aktivzeit, keine Wirkungsdauern und keine Cooldowns.… (+9 more)

### Community 127 - "avoidable.py"
Cohesion: 0.14
Nodes (19): AbilityRule, _build_aliases(), _canonical_name(), classify(), _index(), mechanic_category(), Referenzdaten: welcher Schaden war vermeidbar. WarcraftLogs sagt nur, *wer…, Die Regel zu einer Fähigkeit, oder None wenn keine hinterlegt ist. Reihenfolge:… (+11 more)

### Community 128 - "StorageWatch"
Cohesion: 0.14
Nodes (7): Path, Ausgewertete Kämpfe des Raidlog Analyzers. Bewusst unterhalb von cache(): die…, Beim nächsten Takt neu zählen. Gerufen, wenn sich einer der beiden Ordner…, Sofort zählen, unabhängig vom Takt. Gibt zurück, ob sich die Antwort geändert…, StorageWatch, Vor der ersten Zählung steht der leere Bericht da. Sonst müsste jede lesende…, test_der_bericht_ist_nie_none()

### Community 129 - "raid_context.py"
Cohesion: 0.13
Nodes (18): _error_of(), _moment_of(), outcome_of(), _parse(), datetime, Der Raid-Kontext: welchen Pull habe ich gerade vor mir? **Warum es diese Datei…, Der erste Fehler, der einen Kampf verhindert - in der Reihenfolge der Schritte.…, Wann der Pull war. Die Uhrzeit des **Pulls** zuerst; kennt der Bot sie nicht,… (+10 more)

### Community 130 - "test_class_abilities.py"
Cohesion: 0.13
Nodes (17): _entry(), Die Spec-Referenztabelle ist eine Datentabelle, und Datentabellen altern still:…, Optional heißt talentabhängig und wird nie ergänzt. Eine Spec, die…, Die aktive Schadensminderung ist die eigentliche Leistungskennzahl eines Tanks…, Nicht jede Schadensspezialisierung hat einen DoT, aber keine hat *nichts* -…, Zwei Einträge mit derselben ID wären beim Nachschlagen ein Münzwurf - und der…, Über alle Spezialisierungen hinweg: zwei Fähigkeiten unter einer ID sind ein…, Eine Fähigkeit, die diese Tabelle nicht kennt, darf nicht verschwinden - sie… (+9 more)

### Community 131 - "test_update_visibility.py"
Cohesion: 0.14
Nodes (19): _badge(), Sieht der Nutzer ein wartendes Update, ohne danach zu suchen? Der 2.0-Umbau hat…, "Kein Addon installiert" ist kein Fehler dieser App, sondern ein Schritt, der…, Das Roster ist nicht abgeschaltet - ihm fehlt die Voraussetzung. "AUS" wäre…, Dieselbe Trennung wie `stars == 0` und `at == -1`: aus einer Datenlücke wird…, Eine Zahl und kein Punkt, weil es zwei unabhängige Kanäle gibt und "2" die…, Ohne installiertes Addon steht die **Installation** aus, und das sagt die…, `refresh()` zeichnet. `change_page()` ruft es bei jedem Betreten auf, und der… (+11 more)

### Community 132 - "WarcraftLogsProvider"
Cohesion: 0.13
Nodes (8): `fetch` ist ein Callable ohne Argumente, das ein FetchResult liefert. Es darf…, Ein Abruf. Fehler werden zum Statustext, nicht zur Ausnahme - eine geworfene…, Alter des zwischengespeicherten Berichts in Sekunden. Wird nur unter gehaltenem…, Liest den laufenden WarcraftLogs-Bericht über den Bot., WarcraftLogsProvider, Event, Die Registry ruft jede Fabrik ohne Argumente auf., test_the_factory_builds_a_provider_without_arguments()

### Community 133 - "BackupsSection"
Cohesion: 0.16
Nodes (10): backup_time_text(), Der Zeitpunkt eines Backups als Satzbaustein ("2. September 2026, 14:03 Uhr").…, BackupsSection, Eine der beiden Zeilen aus dem Bericht zeichnen. Gezählt und formuliert wird in…, Was der Rückweg gerade anbieten kann. Drei Fälle, drei Sätze - und keiner davon…, Nach dem Aufräumen sofort neu zählen lassen. Ohne das stünde die Meldung ("hier…, Den Spielstand aus dem jüngsten Backup zurückschreiben. Die Rückfrage nennt das…, Eine erfundene Uhrzeit wäre schlechter als gar keine. (+2 more)

### Community 134 - "extract_variable_body"
Cohesion: 0.17
Nodes (17): extract_variable_body(), Gegenstück zu upsert_variable(): gibt NUR den Inhalt zwischen den äußeren…, Schreibt WoW die Datei, während wir sie zusammenbauen, wird nicht ersetzt - und…, Wer den Zeitraum dreimal hintereinander trifft, schreibt gerade fortlaufend.…, _saved_variables(), test_extract_variable_body_finds_simple_block(), test_extract_variable_body_ignores_braces_inside_strings(), test_extract_variable_body_raises_on_unbalanced_braces() (+9 more)

### Community 135 - "SourceView"
Cohesion: 0.18
Nodes (7): QWidget, Den jüngsten Bericht wählen. Seine Pulls lädt der Dienst daraufhin selbst nach…, Die Pulls dieser Sitzung nachziehen. Getrennt von `_refresh()` und vom Raid…, Ein Knopf, der nichts trifft, wird abgeschaltet und nicht versteckt - *lock,…, Der gemeinsame Eingang aller Ansichten. Diese hier zeigt keinen Snapshot - sie…, Die Auswahl. Eine Ansicht, kein Ort - und kein Fenster., SourceView

### Community 136 - "NavigationItem"
Cohesion: 0.14
Nodes (6): QWidget, Koordinator: linke Unternavigation (Text) + rechter Inhalt, siehe Design's…, SettingsPage, NavigationItem, QFrame, Text-Navigationselement, wie im Design's `.nav-item` (Settings-…

### Community 137 - "_Row"
Cohesion: 0.14
Nodes (8): _FightRow, QFrame, Denselben Weg gehen wie ein Klick - für die Tests und für einen späteren…, Ein Bericht in der linken Spalte., Ein Pull in der rechten Spalte., Eine anklickbare Zeile - Grundform für Bericht und Pull. `mousePressEvent`…, _ReportRow, _Row

### Community 138 - "RaidContextHeader"
Cohesion: 0.17
Nodes (7): RaidContextHeader, Boss, Pull, Ausgang, Zeitpunkt, Charakter - und die zwei Knöpfe, die von hier…, Unter 980 px stehen Kennung und Bedienelemente untereinander. Nebeneinander…, Von aussen einen Charakter wählen - der Sprung aus der Analyse ("diesen Spieler…, Den Kopf aus dem Kontext beschriften. `snapshot` ist optional und nur eine…, Die Auswahlliste nur dann neu füllen, wenn sich der Raid tatsächlich geändert…, Nennt den zuletzt vom Spiel gemeldeten Charakter - und sagt, wenn eine Auswahl…

### Community 139 - "SyncReader"
Cohesion: 0.25
Nodes (9): Path, Gibt NUR den Inhalt der WeintCompanionDB-Variable zurück, nicht die ganze…, SyncReader, _saved_variables_file(), test_get_messages_parses_valid_queue(), test_get_messages_skips_malformed_message_without_crashing(), test_read_recovers_from_unbalanced_braces(), test_remove_message_preserves_other_variable_and_is_atomic() (+1 more)

### Community 140 - "data/encounters.py"
Cohesion: 0.13
Nodes (16): all_encounter_names(), all_instances(), difficulty_name(), instance_for(), instance_size(), lookup(), position_for(), Referenzdaten zu den Raid-Encountern von *World of Warcraft: Forever*. **Die… (+8 more)

### Community 141 - "test_buff_uptimes.py"
Cohesion: 0.19
Nodes (16): Eine Zeile der Tank-Übersicht., TankEntry, Eigene Buffs - die Kennzahl, an der die Tankbewertung hing. Vorher gab es im…, Ohne diese Zeilen wäre die Simulation kein Beweis mehr für den Vertrag: sie…, Der Kern: dieselbe Aktivzeit, einmal mit guter und einmal mit schlechter…, Bei den HoTs abgelegt würden sie nur für Heiler ausgewertet, bei den DoTs…, `has_analysis` ist der einzige Schalter, mit dem die Oberfläche eine ganze…, _snapshot() (+8 more)

### Community 142 - "RaidDay"
Cohesion: 0.16
Nodes (11): _parse_moment(), datetime, RaidDay, Ein Termin des laufenden Raids., Wie viele Zusagen je Rolle - nur aus dem gemeldeten Roster. Ein leeres Ergebnis…, Ob die Zusammensetzung überhaupt bekannt ist. Ein Roster ohne eine einzige…, Restzeit in Minuten; negativ, wenn der Termin begonnen hat. `None` ohne…, Alle noch bevorstehenden Termine, der nächste zuerst. **Warum die Uebersicht… (+3 more)

### Community 143 - "RaidSchedule"
Cohesion: 0.15
Nodes (10): _parse_others(), RaidSchedule, Was der Bot über den laufenden Raid weiß. `known` ist die eine Frage, die die…, Dieser Raid und die übrigen, in der Reihenfolge des Bots - der nächste zuerst., Die weiteren gleichzeitig laufenden Raids. **Warum das rekursiv über…, _appointment_keys(), RaidScheduleSync, Der Termin ohne die Anmeldezahlen - Kennung und Startzeitpunkt je Tag.… (+2 more)

### Community 144 - "._announce_storage"
Cohesion: 0.14
Nodes (9): Eine Meldung unten rechts einblenden. Der Weg für alles, was bisher ein Dialog…, Eine Prüfung ist durch - die Anzeige nachziehen. Nur die **sichtbare** Seite:…, Ein gefundenes Update einmal als Meldung einblenden. Der dritte Weg neben der…, Einmal sagen, wenn sich Downloads oder Backups anhäufen. Jede Addon-…, Dieselbe Nachricht als Sprechblase - nur, wenn das Fenster gerade nicht zu…, Der Grund als Einblendung, wenn eine Installation scheitert. Nur bei einem…, Eine Seite, deren `refresh()` selbst eine Prüfung anstösst, schliesst einen…, test_a_page_refresh_cannot_retrigger_the_refresh() (+1 more)

### Community 145 - "DiscordSection"
Cohesion: 0.15
Nodes (7): _BotProbeBridge, _DiscordLoginBridge, DiscordSection, QObject, QWidget, Meldet das Ergebnis des Discord-Logins thread-sicher an den Hauptthread zurück…, Meldet das Ergebnis der Erreichbarkeitsprüfung zurück in den Hauptthread -…

### Community 146 - "ThemeManager"
Cohesion: 0.15
Nodes (6): QObject, Die aktive Akzentvariante als {"base", "light", "onBase"}., Nur die ausdrueckliche Wahl des Nutzers - das, was der Schalter in den…, Akzent, Dichte und Bewegungsvorgabe - lesbar von ueberall, aenderbar ueber die…, Die gespeicherten Werte uebernehmen. Unbekannte Werte fallen still auf die…, ThemeManager

### Community 147 - "test_last_pull_card.py"
Cohesion: 0.12
Nodes (12): card(), fixture, qt_app(), Die Karte "Dein letzter Pull" auf der Übersicht. Bis 3.6.0 hatte sie einen…, Ein Pull dieser Sitzung hat keinen Bericht - er lief live mit. Eine halbe…, *lock, don't hide*: die Knöpfe bleiben stehen, sind aber abgeschaltet. Ein…, Ein "schwächster Bereich" ohne Auswertung wäre geraten, und die leere…, Der Fall "es gibt wirklich keinen": kein Pull in dieser Sitzung, kein Bericht… (+4 more)

### Community 148 - "test_spec_table.py"
Cohesion: 0.15
Nodes (15): analyzer_data, normalize_spec(), Die Bezeichnung in der Schreibweise, die der Rest der Anwendung benutzt…, Die Spezialisierungstabelle. Sie schließt einen Fehler, der lange nicht…, Dieselbe Regel wie bei den Klassennamen: ein künftiger Patch soll einen Spieler…, Der eigentliche Zweck: eine Bot-Antwort in der Schreibweise von WarcraftLogs…, Nur der Bot kennt die Rangliste, aus der die Rolle stammt - die Spezialisierung…, Derselbe Talentbaum trägt Katze und Bär; welche von beiden jemand gerade ist,… (+7 more)

### Community 149 - "academy_dummy_sync.py"
Cohesion: 0.18
Nodes (15): _parse_date(), practice_for_lessons(), practice_payload(), practice_text(), Rotationstrainer-Sitzungen, wie sie das Addon zurückmeldet. Bewusst ein eigenes…, Der heutige Stand einer gespeicherten Serie. `record` ist ein Eintrag aus…, Der Satz zur Serie - leer, wenn noch nie geübt wurde. Vier Lagen, vier Sätze:…, Die Übungsserien eines Charakters, so wie das Addon sie liest. Geschickt wird… (+7 more)

### Community 150 - "pytest"
Cohesion: 0.12
Nodes (15): pytest, Die Seitenregistrierung ist die Stelle, an der ein Fehler am teuersten wäre:…, Das ist die Bedingung dafür, dass ein Perspektivwechsel den Pull nicht…, pageRequested ist ein Signal(int) und setCurrentIndex erwartet ein int - PageId…, Die Werte SIND die Indizes im QStackedWidget. Eine Lücke oder ein Versatz würde…, Die vom Produkt vorgegebene Reihenfolge der Hauptbereiche (WeintCompanion 4.0,…, Die Zahl selbst ist die Aussage: "wo muss ich jetzt hin" entstand daraus, dass…, Sie stehen in Tiefenverweisen. Eine 2 in einem Signal ist beim nächsten Umbau… (+7 more)

### Community 151 - "_run"
Cohesion: 0.12
Nodes (10): _Config, _Manager, `show_whats_new_if_needed()` ohne Fenster: der Dialog wird durch eine Attrappe…, Der eigentliche Grund für `TOUR_EDITION`. Wer die App seit 1.0 benutzt, hat…, Ein kaputter Wert in der Konfiguration darf die Einführung nicht verschlucken -…, _run(), test_a_long_time_user_gets_the_rewritten_tour(), test_an_ordinary_update_still_shows_the_changelog() (+2 more)

### Community 152 - "Autostart"
Cohesion: 0.21
Nodes (5): Autostart, Path, Verwaltet den Autostart-Eintrag beim Systemstart - Windows über den…, Schreibt (bzw. entfernt) den Autostart-Eintrag. Gibt False zurück, falls die…, Im Bundle (PyInstaller) der eigentliche Programmpfad (AppImage bzw. .exe), in…

### Community 153 - "Skeleton"
Cohesion: 0.15
Nodes (7): QWidget, Mehrere Skelette samt der 250-ms-Verzögerung. Der Aufrufer schaltet `begin()` /…, Ein Abruf hat begonnen. Sichtbar wird das Skelett erst, wenn er länger als 250…, Der Abruf ist beendet - gleich, ob erfolgreich oder nicht., Eine einzelne Skelettfläche. `height` ist 12 px für eine Textzeile oder die…, Skeleton, SkeletonGroup

### Community 154 - "known_encounters"
Cohesion: 0.14
Nodes (14): alias_ability(), known_encounters(), Kämpfe mit hinterlegten Referenzdaten - die Oberfläche kann damit erklären,…, Der englische Fähigkeitsname zu einem deutschen Fehlertext des Bots, oder ""…, Eine Tabelle mit ausschließlich vermeidbaren Fähigkeiten wäre verdächtig:…, Ein Fehler ohne Hinweis ist ein Vorwurf ohne Lernwert - genau das, was die…, Die Übersetzungstabelle für Bot-Texte wird aus den Labels abgeleitet. Zwei…, Sie von Hand zu pflegen wäre bei über achtzig Regeln eine zweite Liste, die… (+6 more)

### Community 155 - "read_changelog_sections"
Cohesion: 0.26
Nodes (13): Liest CHANGELOG.md und gibt die Abschnitte zwischen (exklusiv) "since_version"…, Zerlegt den CHANGELOG-Text in (Version, Body)-Paare, in der Reihenfolge der…, read_changelog_sections(), _split_sections(), Das "Was ist neu"-Fenster liest über denselben Zerleger. Ein Umbau, der ihn…, test_read_respects_limit(), test_read_returns_empty_when_file_missing(), test_read_returns_empty_when_version_not_found() (+5 more)

### Community 156 - "WarcraftLogsArchiveClient"
Cohesion: 0.19
Nodes (7): _detail_of(), Liest Report- und Fight-Listen sowie einzelne vergangene Fights beim Bot., Gemeinsamer HTTP-Teil aller Endpunkte. Liefert (status_code, body, reason).…, Liefert dieselbe Ergebnisform wie WarcraftLogsClient.fetch() - ein FetchResult…, Die Zeitleiste eines Pulls für die Wiedergabe. Bewusst ein eigener Endpunkt…, Der `detail`-Text einer Fehlerantwort des Bots, sofern vorhanden. Wirft nie:…, WarcraftLogsArchiveClient

### Community 157 - "_Swatch"
Cohesion: 0.18
Nodes (4): AccentSwatch, Eine Vorschaukarte für eine Akzentvariante., Gemeinsames Verhalten: anklickbar, zeigt "GEWÄHLT", hebt sich in der…, _Swatch

### Community 158 - "nav"
Cohesion: 0.22
Nodes (10): _app(), card(), _Config, _Manager, nav(), _pump(), fixture, Und zwar auch dann, wenn die Einstellung umgelegt wird, **während** die Karte… (+2 more)

### Community 159 - "build_report_list"
Cohesion: 0.15
Nodes (11): build_report_list(), _format_report_date(), ISO-Zeitstempel (UTC, vom Bot geliefert) in die lokale Zeitzone dieses Rechners…, Übersetzt die Antwort von GET /companion/warcraftlogs/reports. Einträge ohne…, Ohne Code lässt sich der Report später nicht abrufen - ein Eintrag wäre nur ein…, test_build_report_list_drops_entries_without_a_code(), test_build_report_list_maps_known_fields(), test_build_report_list_survives_malformed_input() (+3 more)

### Community 160 - "WhatsNewDialog"
Cohesion: 0.15
Nodes (7): QDialog, Das Fenster selbst. Mit nur einer Seite blendet sich die Zurück/Weiter-…, Nach vorn holen. Ein modaler Dialog, den man nicht sieht, ist kein Dialog mehr,…, Die Höhe des Sichtfelds steht erst fest, wenn Qt das Fenster ausgelegt hat - im…, WhatsNewDialog, Übersprungen wird die Tour, nicht das Changelog. Das Popup nach einem Update…, test_changelog_mode_has_no_skip_button()

### Community 161 - "test_motion.py"
Cohesion: 0.15
Nodes (11): fixture, Bewegung. Zwei Regeln werden hier festgehalten, weil ihre Verletzung stumm…, Ein Abruf unter 250 ms zeigt nie ein Skelett - sonst blitzt bei jedem…, Ein eigener ThemeManager je Test - nicht das Singleton aus `theme()`, damit ein…, Die Zahlen aus §3 des Entwurfs. Sie stehen hier ein zweites Mal, damit ein…, Nutzerwahl ODER Systemvorgabe - beide sagen dasselbe aus., test_an_unknown_token_costs_no_animation_instead_of_crashing(), test_durations_match_the_specification() (+3 more)

### Community 162 - "damage.py"
Cohesion: 0.17
Nodes (11): _avoidable_damage(), _avoidable_hits(), _avoidable_share(), bot_mechanics(), has_usable_classification(), _mentions_taken_ability(), Erhaltenen Schaden einordnen und daraus Mechanikfehler ableiten. Hier wird aus…, Ob der Fehler eine Fähigkeit betrifft, die der Bot für denselben Spieler schon… (+3 more)

### Community 163 - "LessonResult"
Cohesion: 0.17
Nodes (5): LessonResult, Das Gesamturteil zu einer Lektion. Kombinationsregel (siehe…, Der erste Moment, an dem sich ein gescheitertes Kriterium festmacht - das…, _clock(), `rating` ist ein `SkillRating`, `item` der offene `PlanItem` dieses Bereichs…

### Community 164 - "FetchResult"
Cohesion: 0.21
Nodes (7): FetchResult, Was ein Abruf zurückgibt. `payload` ist die Antwort des Bots, oder None.…, _create_warcraftlogs_provider(), Verdrahtet die WarcraftLogs-Quelle mit ihrem Abruf. Die Trennung ist Absicht:…, Holt den aktuellen Bericht beim Bot ab., Ein Abruf. Wirft nie: jeder Fehlerfall wird zu einem FetchResult mit…, WarcraftLogsClient

### Community 165 - "best_try"
Cohesion: 0.17
Nodes (10): best_attempt(), best_try(), BossGroup, Alle Pulls eines Bosses innerhalb eines Berichts., Die Zeile über der Gruppe: wie viele Versuche, und wie es ausging. „12 Versuche…, Der beste Versuch einer Reihe von Pulls. Ein Kill schlägt jeden Wipe; unter…, Der beste Versuch über den **ganzen** Bericht, Bosse hinweg. `best_try()`…, Gleicher Anteil, längerer Kampf: dort ist mehr passiert. (+2 more)

### Community 166 - "ReplayState"
Cohesion: 0.20
Nodes (4): _clock(), Zustandswerte des Raid-Kontexts: die drei Modi (live, archive, replay) und die…, Zustand der Wiedergabe - der Wert, den `ReplayBar` unverändert übernimmt.…, ReplayState

### Community 167 - "_render_emphasis"
Cohesion: 0.17
Nodes (11): `**fett**` wird fett, `*kursiv*` kursiv, Absätze bleiben Absätze. Bewusst kein…, _render_emphasis(), Der Fließtext geht als Rich Text ins Label. Ein `<` in einem Satz würde dort…, Der Text der Tour benutzt zwei Auszeichnungen: `**fett**` betont einen Satz,…, Ein einzelner Stern in einem Satz ist ein Stern - ein halb geöffnetes Tag nähme…, Der Text geht als Rich Text ins Label; ein `<` in einem Satz nähme ihm sonst…, test_an_unpaired_asterisk_leaves_no_open_tag(), test_both_kinds_of_emphasis_become_tags() (+3 more)

### Community 168 - "ModulesSection"
Cohesion: 0.24
Nodes (4): _format_size(), ModulesSection, Zustandstext der Quelle. Läuft sie gerade (WeintTV oder Academy sind geöffnet),…, Ein- und Ausschalten der Zusatzmodule sowie Diagnose der Datenquelle, aus der…

### Community 169 - "page"
Cohesion: 0.18
Nodes (8): nothing(), page(), archive_state(), current(), __init__(), replay_state(), pull(), fixture

### Community 170 - "encounter_meta"
Cohesion: 0.18
Nodes (9): average_text(), encounter_meta(), Boss, Schwierigkeit, Pull, Ausgang und Durchschnittsnote - so weit bekannt.…, Nur die Durchschnittsnote - "Ø 3,7/5", sonst leerer String. Für den Kopf der…, `average_stars` ist 0,0, sobald kein Bereich Daten trägt. "Ø 0,0/5" wäre dort…, Derselbe Boss heroisch und normal sind zwei verschiedene Ansprüche, und ein…, test_an_unrated_profile_gets_no_average_because_zero_means_no_data(), test_the_header_names_difficulty_and_outcome() (+1 more)

### Community 171 - "Trend"
Cohesion: 0.18
Nodes (3): Eine Linie der Lernkurve. `category` ist "" für die Gesamtlinie (das Mittel…, "Rotation 2,7 → 3,8" - die Legende einer Linie., Trend

### Community 172 - "match"
Cohesion: 0.18
Nodes (10): known_cooldown_seconds(), Die Abklingzeit aus der Fähigkeitstabelle, oder 0.0. 0.0 heisst "unbekannt" und…, _cd(), cooldown_info(), match(), Ein Cooldown, dessen Einsätze für diese Spezialisierung zählen. `cooldown` ist…, Der Eintrag einer Spezialisierung zu einem gemeldeten Namen oder einer Spell-…, Der Cooldown-Eintrag zu einem gemeldeten Namen oder einer Spell-ID - **spec-… (+2 more)

### Community 173 - "CharactersPage"
Cohesion: 0.35
Nodes (3): CharactersPage, Wie viele Twinks ausgeblendet sind - und ab welcher Stufe., Wie viele Charaktere aus einer anderen Spielversion stammen - und wie sie…

### Community 174 - "_Logger"
Cohesion: 0.18
Nodes (3): _Config, _Logger, _State

### Community 175 - "AddonReader"
Cohesion: 0.22
Nodes (4): Path, Der Ablageort der Brückendatei, oder None, wenn das Addon nicht installiert…, AddonReader, `wow_path` ist das Installationsverzeichnis der eingestellten Spielversion -…

### Community 176 - "for_actor"
Cohesion: 0.22
Nodes (8): for_actor(), for_spec(), Der komplette Referenzbestand einer Spezialisierung., Der Referenzbestand einer Spezialisierung, oder None. Unbekanntes liefert None…, Derselbe Zugriff für einen Spieler aus dem Snapshot. Fehlt die Spezialisierung,…, SpecAbilities, Der Live-Endpunkt schickt für Heiler regelmäßig keine Spezialisierung. Wo…, test_the_spec_follows_from_class_and_role_when_it_is_missing()

### Community 177 - "build_movement"
Cohesion: 0.22
Nodes (9): build_movement(), format_meters(), meters_from_units(), Laufwege: Rohkoordinaten in Meter umrechnen. Der ganze Sinn dieser Datei ist,…, Karteneinheiten in Meter. Negative Eingaben ergeben 0.0 - eine Distanz kann…, Eine Laufweg-Zeile aus der Rohsumme., Deutsche Anzeige eines Laufwegs. Gehört hierher und nicht in jedes Widget, das…, build_movement_rows() (+1 more)

### Community 178 - "verdict"
Cohesion: 0.20
Nodes (10): is_avoidable(), Das Urteil zu einer Fähigkeit - VERDICT_UNKNOWN, wenn nichts hinterlegt ist.…, verdict(), Der wichtigste Einzelfall der ganzen Auswertung. Wäre Unbekanntes…, Einen Nahkampfangriff für den Tank "vermeidbar" zu nennen wäre unsinnig - er…, test_an_unknown_ability_is_unknown_and_not_unavoidable(), test_classification_never_raises_on_junk(), test_lookup_is_case_insensitive() (+2 more)

### Community 179 - "bot_url_override_path"
Cohesion: 0.22
Nodes (9): bot_url_override_path(), bot_url_source(), Path, Woher die gerade gültige Adresse stammt. Für die Anzeige in den Einstellungen:…, Wo die Datei mit der abweichenden Adresse liegt. Bewusst über `Paths.base()`…, override_hint(), Die beiden Wege, die Adresse ohne neue Fassung zu ändern - für Protokoll und…, Das Feld auf den gerade gültigen Stand bringen. Nicht Teil von `refresh()`:… (+1 more)

### Community 180 - "backup.py"
Cohesion: 0.27
Nodes (7): BackupManager, Das Sicherheitsnetz vor jeder Aktualisierung. Bis 2.7.1 sicherte es genau das…, Stellt "addon_path" aus einem zuvor mit create_backup() erstellten Zip wieder…, Holt den mitgesicherten Spielstand zurück in den WoW-Ordner. Die jeweils…, Die Einträge eines Bereichs - ohne alles, was aus ihm herausführt. Die Archive…, _safe_members(), ZipFile

### Community 181 - "UpdateWatch"
Cohesion: 0.22
Nodes (5): Was die Oberfläche über wartende Updates anzeigt. Bewusst auch die *Fassungen*…, Prüfen, wenn der Takt es hergibt. Gibt zurück, ob sich an der Antwort etwas…, Eine Prüfung, die woanders gelaufen ist, mitzählen. `full_refresh()` und…, Die nächste Runde wirklich prüfen lassen., UpdateWatch

### Community 182 - "pulse_clock"
Cohesion: 0.27
Nodes (3): pulse_clock(), Die eine Pulsuhr der Anwendung., Als welche Art dieser Punkt pulst - oder None.

### Community 183 - "LastPullCard"
Cohesion: 0.27
Nodes (5): LastPullCard, Dein letzter Pull: Ergebnis, schwächster Bereich, eine Lektion. **Woher er…, Den Tiefenverweis auf **diesen** Pull ausgeben. Bericht und Kampfnummer nur,…, `pull` ist ein `LastPull` - aus der Sitzung oder aus dem Archiv, die Karte…, Der Fokus - oder ehrlich, dass es noch keinen gibt. **Es wird nichts…

### Community 184 - "UpdateRow"
Cohesion: 0.20
Nodes (4): QFrame, Eine Komponente mit wartendem Update: Name, Fassung, Auszug, Knopf. **Warum die…, UpdateRow, build()

### Community 185 - "UpdateCard"
Cohesion: 0.24
Nodes (3): Der Update-Hinweis auf der Übersicht. **Warum er hierher gehört.** Ein…, Nur das Band an der Kante neu anfordern, nicht die Karte. Ein `update()` ohne…, UpdateCard

### Community 186 - "MeterRowList"
Cohesion: 0.24
Nodes (5): _MeterRow, MeterRowList, QWidget, `capacity` legt fest, wie viele Zeilen höchstens dargestellt werden. Mehr…, Der Text, der bei leerer Liste steht. Vergleicht vorher: `setText` prüft nicht…

### Community 188 - "test_addon_repository.py"
Cohesion: 0.24
Nodes (9): _github_updater_calls(), Aus welchem Repository holt diese App das Addon? **Warum es diese Prüfung…, Die Gegenprobe: die App darf sich nicht aus dem Addon-Repository aktualisieren,…, Die sichtbare Hälfte derselben Frage. Ein Knopf "GitHub öffnen", der auf die…, Alle `GitHubUpdater(...)`-Aufrufe einer Datei, als Zuordnung ihrer…, Die eine Zeile, deren Fehlgriff folgenlos aussieht und es nicht ist., test_no_link_in_the_interface_points_at_the_mop_repository(), test_the_addon_comes_from_the_forever_repository() (+1 more)

### Community 189 - "weakest_of"
Cohesion: 0.22
Nodes (8): Der schwächste bewertete Bereich eines aufgezeichneten Pulls - `(Kategorie,…, weakest_of(), Die aufgezeichnete Bewertung **genau dieses** Pulls. Zwei Bedingungen, und…, Null Sterne heissen "keine Daten", nicht "schlecht" - ein unbewerteter Bereich…, Sonst sortierte sich die Antwort zwischen zwei Aufrufen um - dieselbe Regel wie…, test_a_record_without_a_single_rating_has_no_weakest_area(), test_a_tie_is_broken_by_the_fixed_category_order(), test_the_weakest_area_skips_unrated_ones()

### Community 190 - "build_fight_list"
Cohesion: 0.22
Nodes (9): build_fight_list(), Übersetzt die Antwort von GET /companion/warcraftlogs/reports/{code}/fights.…, Trash trägt bei WarcraftLogs `encounter_id == 0` und steht in derselben Liste…, None/String-Einträge und ein leeres Dict (fehlende "id" -> -1, wird verworfen)…, test_build_fight_list_drops_entries_without_a_usable_id(), test_build_fight_list_drops_trash(), test_build_fight_list_labels_a_kill_without_a_percentage(), test_build_fight_list_maps_known_fields() (+1 more)

### Community 191 - "AccessProfileSync"
Cohesion: 0.33
Nodes (3): AccessProfileSync, Duenner Mantel um core.access_roles.build_profile_payload(): holt Zuordnung,…, Gilden-ID und -Name in der Konfiguration hinterlegen. Als Zeichenkette, aus…

### Community 192 - "normalize_bot_url"
Cohesion: 0.22
Nodes (8): normalize_bot_url(), Eine brauchbare Basis-URL - oder "". Verlangt wird ein Schema (http/https) und…, Antwortet der Bot unter dieser Adresse überhaupt? Geprüft wird, was im Feld…, Jede Aufrufstelle hängt ihren Pfad mit führendem Schrägstrich an - aus zweien…, Eine kaputte Adresse würde jeden Abruf stillschweigend scheitern lassen. Der…, test_beide_schemata_zaehlen(), test_der_abschliessende_schraegstrich_faellt_weg(), test_unbrauchbares_wird_uebergangen()

### Community 193 - ".__init__"
Cohesion: 0.28
Nodes (4): _PageStack, Ein Stapel, der so hoch ist wie die Seite, die gerade dran ist - nicht wie die…, Das Sichtfeld, unter das der Stapel nicht schrumpfen soll. Wird vom Fenster…, QStackedWidget

### Community 194 - "SectionCard"
Cohesion: 0.22
Nodes (3): QFrame, Untertitel nachträglich ändern. Gebraucht dort, wo er einen berechneten…, SectionCard

### Community 195 - "BossBar"
Cohesion: 0.25
Nodes (4): BossBar, QWidget, `titles=False` lässt Bossname, Zone/Schwierigkeit und den Pull-Chip weg. Für…, Der Bosslebensbalken, 16 px. Mit einer 2 px breiten weißen Marke an der Kante…

### Community 196 - "_Logger"
Cohesion: 0.22
Nodes (3): _Config, _Logger, _Manager

### Community 197 - "test_a_source_without_a_timeline_offers_no_replay"
Cohesion: 0.22
Nodes (6): Die Gegenprobe: `hasattr(provider, "timeline")` war immer wahr, weil die…, Bis ein Fight gewählt ist, soll die Oberfläche nicht den letzten Live-Stand…, test_a_source_without_a_timeline_offers_no_replay(), snapshot(), test_entering_archive_mode_pins_an_empty_snapshot_immediately(), test_live_poll_does_not_overwrite_a_pinned_archive_snapshot()

### Community 198 - "_hits_payload"
Cohesion: 0.22
Nodes (9): _hits_payload(), Der Bot schickt Treffer mit Zeitpunkt, kein Urteil. Ob ein Treffer vermeidbar…, Fehlt eine Fähigkeit in der Tabelle, ist das Urteil `unknown` - und `unknown`…, Tankschaden gehört zum Job und ist ausdrücklich `unavoidable` - dieselbe Regel…, `avoidable_hits` bleibt gültig: meldet der Bot einen Treffer selbst als…, test_an_unknown_ability_produces_no_accusation(), test_pre_judged_hits_from_the_bot_are_still_accepted(), test_raw_hits_are_judged_by_the_app_not_by_the_bot() (+1 more)

### Community 199 - "_announce"
Cohesion: 0.22
Nodes (9): _announce(), Ruft das echte `MainWindow._announce_storage()` auf einem Platzhalter auf -…, `state_changed` kommt beim Start, bei jedem "Erneut prüfen" und aus dem…, Wer aufgeräumt hat, soll beim nächsten Volllaufen wieder etwas hören - sonst…, test_eine_einzelne_neue_datei_meldet_sich_nicht_erneut(), test_gemeldet_wird_einmal_und_nicht_bei_jedem_durchgang(), test_nach_dem_aufraeumen_zaehlt_der_naechste_ueberlauf_wieder(), test_nach_fuenf_weiteren_dateien_wird_wieder_gemeldet() (+1 more)

### Community 200 - "report_subtitle"
Cohesion: 0.25
Nodes (7): "Gleichgewicht Druid" - die Überschrift des Profils., Wie der Bericht heisst — Titel, sonst Zone, sonst sein Code., Die zweite Zeile eines Berichtseintrags: Zone und Code. Der Code gehört dazu,…, report_subtitle(), report_title(), test_the_report_code_stays_findable_because_discord_links_carry_it(), test_the_zone_is_not_repeated_when_it_is_already_the_title()

### Community 201 - "group_reports_by_day"
Cohesion: 0.25
Nodes (7): group_reports_by_day(), Ein Raidabend mit den Berichten, die an ihm entstanden sind., Berichte nach Tag gebündelt, in der gelieferten Reihenfolge (neueste zuerst).…, ReportDay, Ein geratener Tag wäre von einem echten nicht zu unterscheiden - dieselbe Linie…, test_a_report_without_a_date_lands_at_the_end_and_says_so(), test_reports_are_grouped_by_evening_with_the_weekday_in_front()

### Community 202 - "selection_text"
Cohesion: 0.29
Nodes (7): Ein Satz für die Quellenzeile: was gerade gezeigt wird. Er beantwortet die…, _selected_report(), selection_text(), Der Aufrufer setzt dann seinen eigenen Hinweis - ob das ein Mangel ist, hängt…, _State, test_a_chosen_report_without_a_pull_names_only_the_evening(), test_without_a_selection_the_source_line_stays_empty()

### Community 203 - "test_the_popups_are_queued_once_not_on_every_restore"
Cohesion: 0.25
Nodes (4): Der einzige Ort, an dem die Start-Popups angestoßen werden. **Warum an der…, Genau einmal je Fensterleben - `showEvent` feuert auch nach jedem…, `showEvent` feuert auch nach jedem Wiederherstellen aus dem Tray. Ohne Merker…, test_the_popups_are_queued_once_not_on_every_restore()

### Community 204 - "_ArtworkHeader"
Cohesion: 0.29
Nodes (4): _ArtworkHeader, _hex_to_rgb(), QWidget, Das Ökosystem-Artwork oben im "Über"-Tab - dasselbe Bild, das der…

### Community 205 - "ToastHost"
Cohesion: 0.36
Nodes (3): QWidget, Der Stapel unten rechts im Fenster. Er ist ein Kind des Fensters und **kein**…, ToastHost

### Community 206 - "focus_placeholder"
Cohesion: 0.29
Nodes (8): focus_placeholder(), next_lesson_placeholder(), Was in der Baustellenkarte steht, wenn keine Baustelle da ist. Drei Fälle, drei…, Was in der Karte "nächste Lektion" steht, wenn keine da ist. Zwei Fälle, zwei…, "Bewertet, aber nichts Schwaches" ist eine Auskunft über den Pull und ein Lob -…, "Alle Lektionen erledigt" ohne Kampfdaten ist keine Ungenauigkeit, sondern eine…, test_a_clean_pull_is_praised_and_not_reported_as_a_gap(), test_an_empty_plan_without_data_is_not_called_finished()

### Community 208 - "_Logger"
Cohesion: 0.25
Nodes (3): _Logger, Die vorherigen Schritte haben den Zustand schon verändert. Eine halb…, test_full_refresh_reports_even_when_a_step_fails()

### Community 209 - "test_restart_does_not_leave_a_second_worker_behind"
Cohesion: 0.29
Nodes (8): _fetch_thread_count(), Wartet auf `predicate()`, statt sie nur einmal sofort zu prüfen. Wichtig für…, Der RaidDataService ruft start() bei JEDEM Poll auf - ohne Idempotenz entstünde…, Folgen stop() und start() dicht aufeinander, darf der alte Abruf-Thread nicht…, Zählt NUR lebende Threads mit dem Namen "WarcraftLogsFetch" (den jeder…, test_restart_does_not_leave_a_second_worker_behind(), test_start_is_idempotent_and_starts_only_one_worker(), _wait_until_settled()

### Community 210 - "ring_alpha"
Cohesion: 0.29
Nodes (6): Die Deckkraft des Rings zu einer Phase der Pulsuhr. Eigene Funktion und nicht…, Die Deckkraft, die der Ring in diesem Augenblick tragen soll. `is_reduced()`…, ring_alpha(), ring_strength(), Bei reduzierter Bewegung und bei einem sichtbaren LIVE-Zeichen steht die Uhr,…, test_a_standing_ring_stands_at_full_strength()

### Community 212 - "translations"
Cohesion: 0.33
Nodes (6): Englischer Name -> deutsche Schreibweisen, über alle Specs. Für…, translations(), Der Lektionskatalog nennt Fähigkeiten englisch, ein deutscher Bericht liefert…, Der eigentliche Gegenstand: die Oberfläche muss "keine Angaben" zeigen und darf…, test_an_empty_table_answers_with_nothing_and_never_with_a_guess(), test_translations_reach_the_lesson_matching()

### Community 213 - "._refresh_updates"
Cohesion: 0.33
Nodes (5): _excerpt(), _note_head(), Die Zeile über dem Auszug: **welche Fassung** er beschreibt. Ohne sie ist der…, Die Karte an den Zustand anlegen. Der Auszug kommt aus…, Die ersten Zeilen der Notizen zur **installierten** Fassung. Ohne Notizen ein…

### Community 214 - ".metric"
Cohesion: 0.33
Nodes (3): Die aktive Dichte als Tabelle (row, pad_v, pad_h, ...)., Ein einzelner Dichtewert., Eine Schriftgroesse, um den Dichteversatz verschoben. Mindestens 9 px: bei…

### Community 215 - "page"
Cohesion: 0.33
Nodes (5): _Logger, page(), __init__(), fixture, qt_app()

### Community 216 - "_theme"
Cohesion: 0.33
Nodes (4): _app(), _Config, fixture, _theme()

### Community 217 - "_warn_subscribers"
Cohesion: 0.33
Nodes (6): Wie viele sichtbare Warnquellen die Uhr gerade zählt. Der Zähler ist privat und…, Angemeldet wird bei der Sichtbarkeit, nicht beim Bauen. Die Karte entsteht auf…, `close()` erzeugt auf manchen Plattformen ein zweites Verbergen, und eine Karte…, test_an_already_counted_card_is_not_counted_twice(), test_the_card_only_pulses_while_it_is_visible(), _warn_subscribers()

### Community 218 - "AreaFocus"
Cohesion: 0.40
Nodes (3): AreaFocus, Was die aufgezeichneten Pulls über einen Bereich sagen. `average` ist das…, Bei gleichem Mittel zuerst der Bereich, der **schwächer** wird. Zwei Bereiche…

### Community 219 - "build_metrics"
Cohesion: 0.40
Nodes (5): build_metrics(), _entries(), Baut eine sortierte Rangliste mit Anteilen. Nur noch eine Weiterleitung: die…, Teilt das Roster in Schadens- und Heilrangliste. Die Aufteilung folgt der Rolle…, test_build_metrics_handles_an_empty_roster()

### Community 220 - "class_name"
Cohesion: 0.40
Nodes (5): class_name(), Klassenname in der Schreibweise des Combat-Logs. Unbekannte Klassen werden…, WarcraftLogs schreibt "DeathKnight", der Rest der Anwendung "Death Knight".…, test_class_names_are_normalised_to_the_combat_log_spelling(), test_unknown_classes_survive_unchanged()

### Community 221 - "main"
Cohesion: 0.50
Nodes (5): main(), _show_main_window(), _stage(), Ob das Betriebssystem "weniger Bewegung" vorgibt. Qt hat dafuer bis heute keine…, _system_prefers_reduced_motion()

### Community 222 - ".newest_with_saved_variables"
Cohesion: 0.50
Nodes (3): Path, Alle Backups, das jüngste zuerst., Das jüngste Backup, das einen Spielstand enthält - oder None. Backups aus einer…

### Community 223 - "show_whats_new_if_needed"
Cohesion: 0.40
Nodes (4): _build_changelog_pages(), Wird einmal beim Start aufgerufen (siehe gui/main_window.py). Drei Fälle, in…, show_whats_new_if_needed(), "Was ist neu", danach ggf. der Discord-Verknüpfungshinweis - beide unabhängig…

### Community 225 - "should_animate_number"
Cohesion: 0.40
Nodes (5): Ob eine Zahlenaenderung animiert werden darf. Grosse Spruenge werden gesetzt:…, should_animate_number(), Der erste Messwert eines Pulls kommt aus dem Nichts. Eine Zahl, die 240 ms lang…, test_identical_values_are_not_animated(), test_large_number_jumps_are_set_instead_of_animated()

### Community 228 - "known_specs"
Cohesion: 0.50
Nodes (4): known_specs(), (Klasse, Spezialisierung) aller hinterlegten Einträge - für Tests und die…, Fällt dieser Test um, ist die Tabelle gefüllt worden - dann sind die…, test_the_table_is_empty_and_that_is_on_purpose()

### Community 229 - ".time_label"
Cohesion: 0.50
Nodes (3): _format_report_time(), Die Uhrzeit des Pulls, in der Zeitzone dieses Rechners., Nur die Uhrzeit desselben Zeitstempels - für die Pull-Liste, wo das Datum…

### Community 230 - "analysis_guide.py"
Cohesion: 0.50
Nodes (3): GuideSection, Was das Raid Center beantwortet - in Worten. **Warum diese Datei existiert.**…, Eine Ansicht, in drei Zeilen erklärt.

### Community 233 - "show_tour"
Cohesion: 0.50
Nodes (4): Die Fassung der Tour vermerken. Gesehen ist gesehen: vermerkt wird beim Zeigen…, Zeigt den Rundgang unabhängig vom gespeicherten Zustand - für den Knopf in…, _remember_tour(), show_tour()

### Community 234 - ".show_lesson"
Cohesion: 0.50
Nodes (3): Der Scrollbereich, in dem dieses Widget liegt - oder `None`. Über den…, Die Lektionskarte zu `lesson_id` in den Blick holen. Kein Seitenwechsel und…, _scroll_area_of()

### Community 235 - "suspend_value_animation"
Cohesion: 0.50
Nodes (4): Ob Zahlen- und Balkenbewegung bei dieser Datenrate auszusetzen ist. Gilt fuer…, suspend_value_animation(), Die Wiedergabe tickt mit 4 Hz, eine Live-Quelle mit rund 1 Hz., test_playback_rates_suspend_value_animation()

### Community 236 - "accent"
Cohesion: 0.50
Nodes (4): accent(), Die Akzentvariante zu `name`, mit Rückfall auf die Voreinstellung. Ein…, `config.json` ist eine Datei, die von Hand bearbeitet werden kann. Ein…, test_unknown_accent_falls_back_instead_of_failing()

### Community 238 - "test_a_stale_fights_result_is_discarded"
Cohesion: 0.50
Nodes (3): Wird zwischen Anfrage und Antwort bereits ein anderer Report gewählt, gehört…, test_a_stale_fights_result_is_discarded(), fetch_fights()

### Community 240 - "_DialogPage"
Cohesion: 0.67
Nodes (3): _DialogPage, QWidget, Eine Seite: Symbol, Kapitel, Titel, Fließtext, optionaler Knopf. Der Fließtext…

### Community 241 - "tinted"
Cohesion: 0.67
Nodes (3): Dasselbe als QIcon - fuer alles, was ein Icon erwartet (Knoepfe, Tray,…, tinted(), QIcon

### Community 243 - "_shutdown_services"
Cohesion: 0.67
Nodes (3): fixture, Nach jedem Test alle erzeugten Dienste beenden. Nicht bloß Ordnungsliebe: ein…, _shutdown_services()

### Community 244 - "qt_app"
Cohesion: 0.67
Nodes (3): fixture, qt_app(), Eine QApplication fuer die Prueflinge, die wirklich zeichnen. Dieselbe Bauform…

## Knowledge Gaps
- **3 isolated node(s):** `updater.sh script`, `build_appimage.sh script`, `build_linux.sh script`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2883 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RaidSnapshot` connect `RaidSnapshot` to `HeroButton`, `theme`, `raid_context.py`, `WarcraftLogsProvider`, `MockRaidDataProvider`, `RaidDataService`, `test_academy_progression.py`, `companion_manager.py`, `test_replay.py`, `RaidContextHeader`, `test_raid_data_service.py`, `test_addon_payloads.py`, `test_buff_uptimes.py`, `Actor`, `CooldownUsage`, `test_academy_evaluator.py`, `AcademyService`, `test_addon_analysis_sync.py`, `AnalysisView`, `analyzer/models.py`, `warcraftlogs_payload.py`, `preparation.py`, `test_raid_context.py`, `snapshot_from_payload`, `page`, `UptimeEntry`, `encounter_meta`, `OverlayWindow`, `test_character_report_sync.py`, `test_academy_selection.py`, `test_academy_checks.py`, `checks.py`, `test_a_source_without_a_timeline_offers_no_replay`, `test_academy_empty_state.py`, `test_warcraftlogs_provider.py`, `LearnView`, `LiveView`, `RaidDataProvider`, `_snapshot`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `Paths` connect `Paths` to `StorageWatch`, `theme`, `HeroButton`, `test_character_sheet.py`, `test_install_failure.py`, `BackupsSection`, `test_academy_progression.py`, `companion_manager.py`, `RaidSchedule`, `AcademyService`, `CompanionManager`, `FightSummary`, `DiscordAccountStore`, `LogWidget`, `test_character_report_sync.py`, `bot_url_override_path`, `backup.py`, `test_academy_selection.py`, `test_academy_service.py`, `AddonPage`, `PullRecord`, `test_academy_dummy_sync.py`, `CompanionUpdater`, `_pull_snapshot`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `AcademyService` connect `AcademyService` to `RaidSnapshot`, `test_academy_service.py`, `test_academy_progression.py`, `companion_manager.py`, `page`, `test_analysis_guide.py`, `test_addon_payloads.py`, `test_academy_empty_state.py`, `test_character_report_sync.py`, `_pull_snapshot`, `PullRecord`, `CompanionManager`, `test_academy_selection.py`, `page`, `test_raid_center.py`, `Paths`, `_snapshot`, `test_academy_dummy_sync.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `RaidSnapshot` (e.g. with `build_academy_state()` and `build_weinttv_report()`) actually correct?**
  _`RaidSnapshot` has 76 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `MockRaidDataProvider` (e.g. with `ActivityEntry` and `Actor`) actually correct?**
  _`MockRaidDataProvider` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `updater.sh script`, `build_appimage.sh script`, `build_linux.sh script` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `HeroButton` be split into smaller, more focused modules?**
  _Cohesion score 0.022190339550454328 - nodes in this community are weakly interconnected._