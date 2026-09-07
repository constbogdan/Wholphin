
  # TV multi-season
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario tv_multi_season

# Movie lifecycle states
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario movie_states

# Mixed
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario mixed

# Empty row
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario empty

# Back to real data
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario real

  & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario focus_before

  & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario focus_card_removed

   & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am broadcast `
  -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver `
  -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE `
  --es scenario focus_row_removed