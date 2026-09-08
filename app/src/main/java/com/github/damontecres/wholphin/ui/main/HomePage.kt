package com.github.damontecres.wholphin.ui.main

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.focusGroup
import androidx.compose.foundation.gestures.LocalBringIntoViewSpec
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusProperties
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.input.key.KeyEvent
import androidx.compose.ui.input.key.onKeyEvent
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.DpSize
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import androidx.lifecycle.compose.LifecycleStartEffect
import androidx.tv.material3.Card
import androidx.tv.material3.CardDefaults
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.github.damontecres.wholphin.R
import com.github.damontecres.wholphin.data.model.BaseItem
import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.DiscoverItem
import com.github.damontecres.wholphin.data.model.HomeRowConfig
import com.github.damontecres.wholphin.data.model.HomeRowViewOptions
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.QuickDetailsData
import com.github.damontecres.wholphin.preferences.UserPreferences
import com.github.damontecres.wholphin.ui.AppColors
import com.github.damontecres.wholphin.ui.AspectRatios
import com.github.damontecres.wholphin.ui.Cards
import com.github.damontecres.wholphin.ui.cards.AcquisitionStateIndicator
import com.github.damontecres.wholphin.ui.cards.BannerCard
import com.github.damontecres.wholphin.ui.cards.BannerCardWithTitle
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.cards.CardMediaPresentation
import com.github.damontecres.wholphin.ui.cards.GenreCard
import com.github.damontecres.wholphin.ui.cards.ItemCardImage
import com.github.damontecres.wholphin.ui.cards.ItemRow
import com.github.damontecres.wholphin.ui.cards.StudioCard
import com.github.damontecres.wholphin.ui.cards.ViewMoreCard
import com.github.damontecres.wholphin.ui.components.CircularProgress
import com.github.damontecres.wholphin.ui.components.ContextMenu
import com.github.damontecres.wholphin.ui.components.ContextMenuActions
import com.github.damontecres.wholphin.ui.components.ContextMenuDialog
import com.github.damontecres.wholphin.ui.components.EpisodeName
import com.github.damontecres.wholphin.ui.components.ErrorMessage
import com.github.damontecres.wholphin.ui.components.FocusableItemRow
import com.github.damontecres.wholphin.ui.components.HeaderUtils
import com.github.damontecres.wholphin.ui.components.LoadingPage
import com.github.damontecres.wholphin.ui.components.QuickDetails
import com.github.damontecres.wholphin.ui.components.TitleOrLogo
import com.github.damontecres.wholphin.ui.components.rememberLogoUrl
import com.github.damontecres.wholphin.ui.data.AddPlaylistViewModel
import com.github.damontecres.wholphin.ui.data.ItemDetailsDialog
import com.github.damontecres.wholphin.ui.data.ItemDetailsDialogInfo
import com.github.damontecres.wholphin.ui.data.RowColumn
import com.github.damontecres.wholphin.ui.detail.PlaylistDialog
import com.github.damontecres.wholphin.ui.indexOfFirstOrNull
import com.github.damontecres.wholphin.ui.isNotNullOrBlank
import com.github.damontecres.wholphin.ui.nav.Destination
import com.github.damontecres.wholphin.ui.nav.verifiedSeriesDestination
import com.github.damontecres.wholphin.ui.playback.isPlayKeyUp
import com.github.damontecres.wholphin.ui.playback.playable
import com.github.damontecres.wholphin.ui.playback.scale
import com.github.damontecres.wholphin.ui.rememberPosition
import com.github.damontecres.wholphin.ui.tryRequestFocus
import com.github.damontecres.wholphin.ui.util.ScrollToTopBringIntoViewSpec
import com.github.damontecres.wholphin.util.HomeRowLoadingState
import com.github.damontecres.wholphin.util.LoadingState
import kotlinx.coroutines.delay
import org.jellyfin.sdk.model.DateTime
import org.jellyfin.sdk.model.api.BaseItemKind
import timber.log.Timber
import java.util.UUID
import kotlin.time.Duration

@Composable
fun HomePage(
    preferences: UserPreferences,
    modifier: Modifier = Modifier,
    viewModel: HomeViewModel = hiltViewModel(),
    playlistViewModel: AddPlaylistViewModel = hiltViewModel(),
) {
    val context = LocalContext.current
    LifecycleStartEffect(Unit) {
        viewModel.init()
        onStopOrDispose { }
    }
    val state by viewModel.state.collectAsState()
    val loading = state.loadingState
    val refreshing = state.refreshState
    val homeRows = state.homeRows
    val acquiringItems = state.acquiringItems

    when (val state = loading) {
        is LoadingState.Error -> {
            ErrorMessage(state, modifier)
        }

        LoadingState.Loading,
        LoadingState.Pending,
        -> {
            LoadingPage(modifier)
        }

        LoadingState.Success -> {
            var showContextMenu by remember { mutableStateOf<ContextMenu?>(null) }
            var showPlaylistDialog by remember { mutableStateOf<UUID?>(null) }
            var overviewDialog by remember { mutableStateOf<ItemDetailsDialogInfo?>(null) }

            val playlistState by playlistViewModel.playlistState.collectAsState()
            var position by rememberPosition()
            var acquiringFocusType by rememberSaveable { mutableStateOf<String?>(null) }
            var acquiringFocusTmdbId by rememberSaveable { mutableStateOf<Int?>(null) }
            var acquiringFocusSeasonNumber by rememberSaveable { mutableStateOf<Int?>(null) }
            val preferredAcquiringKey =
                acquiringFocusType?.let { type ->
                    acquiringFocusTmdbId?.let { tmdbId ->
                        runCatching {
                            val catalog = MediaKey.Catalog(CatalogMediaType.valueOf(type), tmdbId)
                            acquiringFocusSeasonNumber?.let { MediaKey.Season(catalog, it) } ?: catalog
                        }.getOrNull()
                    }
                }

            val onFocusPosition = remember { { it: RowColumn -> position = it } }
            val currentHomePrefs by rememberUpdatedState(preferences.appPreferences.homePagePreferences)
            val onClickItem =
                remember {
                    { clickedPosition: RowColumn, item: BaseItem ->
                        position = clickedPosition
                        if (currentHomePrefs.clickToPlay &&
                            homeRows.getOrNull(clickedPosition.row)?.isContinueWatchingNextUp == true
                        ) {
                            viewModel.navigationManager.navigateTo(Destination.Playback(item))
                        } else {
                            viewModel.navigationManager.navigateTo(item.destination())
                        }
                    }
                }
            val onLongClickItem =
                remember {
                    { clickedPosition: RowColumn, item: BaseItem ->
                        position = clickedPosition
                        val row =
                            (homeRows.getOrNull(clickedPosition.row) as? HomeRowLoadingState.Success)
                        val canRemoveContinueWatching =
                            row?.rowType is HomeRowConfig.ContinueWatching || row?.rowType is HomeRowConfig.ContinueWatchingCombined
                        val canRemoveNextUp =
                            row?.rowType is HomeRowConfig.NextUp || row?.rowType is HomeRowConfig.ContinueWatchingCombined
                        showContextMenu =
                            ContextMenu.ForBaseItem(
                                fromLongClick = true,
                                item = item,
                                chosenStreams = null,
                                showGoTo = true,
                                showStreamChoices = false,
                                canDelete =
                                    viewModel.canDelete(
                                        item,
                                        preferences.appPreferences,
                                    ),
                                canRemoveContinueWatching = canRemoveContinueWatching,
                                canRemoveNextUp = canRemoveNextUp,
                                actions =
                                    ContextMenuActions(
                                        navigateTo = viewModel.navigationManager::navigateTo,
                                        onClickWatch = viewModel::setWatched,
                                        onClickFavorite = viewModel::setFavorite,
                                        onClickAddPlaylist = { itemId ->
                                            playlistViewModel.loadPlaylists()
                                            showPlaylistDialog = itemId
                                        },
                                        onSendMediaInfo = viewModel.serverReportService::sendMediaReportFor,
                                        onDeleteItem = {
                                            viewModel.deleteItem(position, it)
                                        },
                                        onChooseVersion = { _, _ ->
                                            // Not supported on this page
                                        },
                                        onChooseTracks = {
                                            // Not supported on this page
                                        },
                                        onShowOverview = {
                                            overviewDialog = ItemDetailsDialogInfo(it)
                                        },
                                        onClearChosenStreams = {},
                                        onClickRemoveFromNextUp = viewModel::removeFromNextUp,
                                    ),
                            )
                    }
                }
            val onClickPlay =
                remember {
                    { _: RowColumn, item: BaseItem ->
                        viewModel.navigationManager.navigateTo(Destination.Playback(item))
                    }
                }
            val onClickViewMore =
                remember {
                    { _: RowColumn, row: HomeRowLoadingState.Success ->
                        viewModel.navigationManager.navigateTo(
                            Destination.MoreHomeRow(row.title, row.rowType!!, row.items.size),
                        )
                    }
                }

            HomePageContent(
                homeRows = homeRows,
                acquiringItems = acquiringItems,
                preferredAcquiringKey = preferredAcquiringKey,
                onPreferredAcquiringKeyChanged = { key ->
                    acquiringFocusType = key?.homeCatalogMediaType?.name
                    acquiringFocusTmdbId = key?.homeTmdbId
                    acquiringFocusSeasonNumber = (key as? MediaKey.Season)?.seasonNumber
                },
                position = position,
                onFocusPosition = onFocusPosition,
                onClickItem = onClickItem,
                onLongClickItem = onLongClickItem,
                onClickPlay = onClickPlay,
                loadingState = refreshing,
                showClock = preferences.appPreferences.interfacePreferences.showClock,
                onUpdateBackdrop = viewModel::updateBackdrop,
                onUpdateAcquiringBackdrop = viewModel::updateBackdrop,
                onClickAcquiring = { item ->
                    viewModel.navigationManager.navigateTo(item.destination())
                },
                onClickAcquiringMore = {
                    viewModel.navigationManager.navigateTo(homeAcquiringMoreDestination())
                },
                showLogo = preferences.appPreferences.interfacePreferences.showLogos,
                showViewMore = true,
                onClickViewMore = onClickViewMore,
                modifier = modifier,
            )
            overviewDialog?.let { info ->
                ItemDetailsDialog(
                    info = info,
                    showFilePath = false,
                    onDismissRequest = { overviewDialog = null },
                )
            }
            showContextMenu?.let { contextMenu ->
                ContextMenuDialog(
                    onDismissRequest = { showContextMenu = null },
                    getMediaSource = null,
                    contextMenu = contextMenu,
                    preferredSubtitleLanguage = null,
                )
            }
            showPlaylistDialog?.let { itemId ->
                PlaylistDialog(
                    title = stringResource(R.string.add_to_playlist),
                    state = playlistState,
                    onDismissRequest = { showPlaylistDialog = null },
                    onClick = {
                        playlistViewModel.addToPlaylist(it.id, itemId)
                        showPlaylistDialog = null
                    },
                    createEnabled = true,
                    onCreatePlaylist = {
                        playlistViewModel.createPlaylistAndAddItem(it, itemId)
                        showPlaylistDialog = null
                    },
                    onSearch = playlistViewModel::loadPlaylists,
                    elevation = 3.dp,
                )
            }
        }
    }
}

val HomeRowLoadingState?.isContinueWatchingNextUp: Boolean
    get() =
        (this as? HomeRowLoadingState.Success).let { row ->
            row?.rowType is HomeRowConfig.ContinueWatching ||
                row?.rowType is HomeRowConfig.NextUp ||
                row?.rowType is HomeRowConfig.ContinueWatchingCombined
        }

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun HomePageContent(
    homeRows: List<HomeRowLoadingState>,
    position: RowColumn,
    onFocusPosition: (RowColumn) -> Unit,
    onClickItem: (RowColumn, BaseItem) -> Unit,
    onLongClickItem: (RowColumn, BaseItem) -> Unit,
    onClickPlay: (RowColumn, BaseItem) -> Unit,
    showClock: Boolean,
    onUpdateBackdrop: (BaseItem) -> Unit,
    acquiringItems: List<HomeAcquiringItem> = emptyList(),
    preferredAcquiringKey: MediaKey? = null,
    onPreferredAcquiringKeyChanged: (MediaKey?) -> Unit = {},
    onClickAcquiring: (HomeAcquiringItem) -> Unit = {},
    onClickAcquiringMore: () -> Unit = {},
    onUpdateAcquiringBackdrop: (DiscoverItem) -> Unit = {},
    showLogo: Boolean,
    showViewMore: Boolean,
    modifier: Modifier = Modifier,
    loadingState: LoadingState? = null,
    listState: LazyListState = rememberLazyListState(),
    takeFocus: Boolean = true,
    showEmptyRows: Boolean = false,
    headerComposable: @Composable (focusedItem: BaseItem?) -> Unit = { focusedItem ->
        HomePageHeader(
            item = focusedItem,
            showLogo = showLogo,
            modifier = HeaderUtils.modifier,
        )
    },
    onClickViewMore: (RowColumn, HomeRowLoadingState.Success) -> Unit = { _, _ -> },
) {
    val focusedItem =
        remember(homeRows, position) {
            (homeRows.getOrNull(position.row) as? HomeRowLoadingState.Success)?.items?.getOrNull(
                position.column,
            )
        }

    val rowFocusRequesters = remember(homeRows.size) { List(homeRows.size) { FocusRequester() } }
    val acquiringFocusRequesters =
        remember(acquiringItems.map(HomeAcquiringItem::key)) {
            acquiringItems.associate { it.key to FocusRequester() }
        }
    var focusedAcquiringKey by remember { mutableStateOf<MediaKey?>(preferredAcquiringKey) }
    var acquiringHasFocus by remember { mutableStateOf(preferredAcquiringKey != null) }
    var previousAcquiringKeys by remember { mutableStateOf(emptyList<MediaKey>()) }
    var firstFocused by remember { mutableStateOf(false) }

    val currentPosition by rememberUpdatedState(position)
    val currentOnFocusPosition by rememberUpdatedState(onFocusPosition)
    val currentOnClickPlay by rememberUpdatedState(onClickPlay)

    if (takeFocus) {
        LaunchedEffect(homeRows) {
            if (!firstFocused && homeRows.isNotEmpty()) {
                if (preferredAcquiringKey in acquiringItems.map(HomeAcquiringItem::key)) {
                    focusedAcquiringKey = preferredAcquiringKey
                    acquiringFocusRequesters[focusedAcquiringKey]?.tryRequestFocus()
                    firstFocused = true
                } else if (position.row < 0 && acquiringItems.isNotEmpty()) {
                    focusedAcquiringKey = acquiringItems.first().key
                    onPreferredAcquiringKeyChanged(focusedAcquiringKey)
                    acquiringFocusRequesters[focusedAcquiringKey]?.tryRequestFocus()
                    firstFocused = true
                } else if (position.row >= 0) {
                    val index = position.row.coerceIn(0, rowFocusRequesters.lastIndex)
                    rowFocusRequesters.getOrNull(index)?.tryRequestFocus()
                    firstFocused = true
                } else {
                    // Waiting for the first home row to load, then focus on it
                    homeRows
                        .indexOfFirstOrNull { it is HomeRowLoadingState.Success && it.items.isNotEmpty() }
                        ?.let {
                            rowFocusRequesters[it].tryRequestFocus()
                            firstFocused = true
                            delay(50)
                            listState.scrollToItem(it)
                        }
                }
            }
        }
    }
    LaunchedEffect(acquiringItems) {
        val currentKeys = acquiringItems.map(HomeAcquiringItem::key)
        when (
            val resolution =
                resolveAcquiringFocus(
                    acquiringHadFocus = acquiringHasFocus,
                    previousKeys = previousAcquiringKeys,
                    currentKeys = currentKeys,
                    focusedKey = focusedAcquiringKey,
                )
        ) {
            is AcquiringFocusResolution.Card -> {
                focusedAcquiringKey = resolution.key
                onPreferredAcquiringKeyChanged(resolution.key)
                acquiringFocusRequesters[resolution.key]?.tryRequestFocus()
            }

            AcquiringFocusResolution.ConfiguredFallback -> {
                acquiringHasFocus = false
                onPreferredAcquiringKeyChanged(null)
                homeRows
                    .indexOfFirstOrNull { it is HomeRowLoadingState.Success && it.items.isNotEmpty() }
                    ?.let { rowFocusRequesters[it].tryRequestFocus() }
            }

            AcquiringFocusResolution.Unchanged -> {
                Unit
            }
        }
        previousAcquiringKeys = currentKeys
    }
    val focusedAcquiringItem =
        remember(acquiringItems, focusedAcquiringKey, acquiringHasFocus) {
            if (acquiringHasFocus) acquiringItems.firstOrNull { it.key == focusedAcquiringKey } else null
        }
    LaunchedEffect(onUpdateBackdrop, focusedItem, focusedAcquiringItem) {
        if (focusedAcquiringItem != null) {
            onUpdateAcquiringBackdrop(focusedAcquiringItem.item)
        } else {
            focusedItem?.let { onUpdateBackdrop.invoke(it) }
        }
    }
    Box(modifier = modifier) {
        Column(
            modifier =
                Modifier
                    .focusProperties {
                        onEnter = {
                            if (acquiringHasFocus && acquiringItems.isNotEmpty()) {
                                acquiringFocusRequesters[focusedAcquiringKey]?.tryRequestFocus()
                            } else {
                                rowFocusRequesters.getOrNull(currentPosition.row)?.tryRequestFocus()
                            }
                        }
                    }.fillMaxSize(),
        ) {
            if (focusedAcquiringItem != null) {
                HomeAcquiringHeader(focusedAcquiringItem.item, showLogo, HeaderUtils.modifier)
            } else {
                headerComposable.invoke(focusedItem)
            }

            val density = LocalDensity.current
            val spaceAbovePx =
                remember(density) {
                    with(density) {
                        // The size of the row titles & spacing
                        50.dp.toPx()
                    }
                }
            val defaultBringIntoViewSpec = LocalBringIntoViewSpec.current
            CompositionLocalProvider(
                LocalBringIntoViewSpec provides ScrollToTopBringIntoViewSpec(spaceAbovePx),
            ) {
                LazyColumn(
                    state = listState,
                    verticalArrangement = Arrangement.spacedBy(0.dp),
                    contentPadding =
                        PaddingValues(
                            bottom = Cards.height2x3,
                        ),
                    modifier =
                        Modifier
                            .focusRestorer(),
                ) {
                    if (acquiringItems.isNotEmpty()) {
                        item(key = HOME_ACQUIRING_ROW_KEY) {
                            CompositionLocalProvider(
                                LocalBringIntoViewSpec provides defaultBringIntoViewSpec,
                            ) {
                                HomeAcquiringRow(
                                    items = acquiringItems,
                                    focusRequesters = acquiringFocusRequesters,
                                    onClick = onClickAcquiring,
                                    onClickMore = onClickAcquiringMore,
                                    onFocus = { key ->
                                        acquiringHasFocus = true
                                        focusedAcquiringKey = key
                                        onPreferredAcquiringKeyChanged(key)
                                    },
                                    modifier =
                                        Modifier
                                            .animateItem()
                                            .padding(bottom = homeRowBottomPadding),
                                )
                            }
                        }
                    }
                    itemsIndexed(homeRows, key = { index, _ -> configuredHomeRowKey(index) }) { rowIndex, row ->
                        val rowModifier =
                            Modifier
                                .animateItem()
                                .padding(bottom = homeRowBottomPadding)
                        CompositionLocalProvider(
                            LocalBringIntoViewSpec provides defaultBringIntoViewSpec,
                        ) {
                            when (val r = row) {
                                is HomeRowLoadingState.Loading,
                                is HomeRowLoadingState.Pending,
                                -> {
                                    FocusableItemRow(
                                        title = r.title.getString(),
                                        subtitle = stringResource(R.string.loading),
                                        modifier = rowModifier,
                                    )
                                }

                                is HomeRowLoadingState.Error -> {
                                    FocusableItemRow(
                                        title = r.title.getString(),
                                        subtitle = r.localizedMessage,
                                        isError = true,
                                        modifier = rowModifier,
                                    )
                                }

                                is HomeRowLoadingState.Success -> {
                                    if (row.items.isNotEmpty()) {
                                        val viewOptions = row.viewOptions
                                        ItemRow(
                                            title = row.title.getString(),
                                            items = row.items,
                                            onClickItem =
                                                remember(rowIndex, onClickItem) {
                                                    { index, item ->
                                                        onClickItem.invoke(
                                                            RowColumn(
                                                                rowIndex,
                                                                index,
                                                            ),
                                                            item,
                                                        )
                                                    }
                                                },
                                            onLongClickItem =
                                                remember(rowIndex, onLongClickItem) {
                                                    { index, item ->
                                                        onLongClickItem.invoke(
                                                            RowColumn(rowIndex, index),
                                                            item,
                                                        )
                                                    }
                                                },
                                            modifier =
                                                rowModifier
                                                    .fillMaxWidth()
                                                    .focusGroup()
                                                    .focusRequester(rowFocusRequesters[rowIndex]),
                                            horizontalPadding = viewOptions.spacing.dp,
                                            cardContent = { index, item, cardModifier, onClick, onLongClick ->
                                                val onFocus =
                                                    remember(rowIndex, index) {
                                                        { isFocused: Boolean ->
                                                            if (isFocused) {
                                                                acquiringHasFocus = false
                                                                onPreferredAcquiringKeyChanged(null)
                                                                currentOnFocusPosition(
                                                                    RowColumn(
                                                                        rowIndex,
                                                                        index,
                                                                    ),
                                                                )
                                                            }
                                                        }
                                                    }
                                                val onKey =
                                                    remember(item) {
                                                        { event: KeyEvent ->
                                                            if (isPlayKeyUp(event) && item?.type?.playable == true) {
                                                                Timber.v("Clicked play on ${item.id}")
                                                                currentOnClickPlay(
                                                                    currentPosition,
                                                                    item,
                                                                )
                                                                true
                                                            } else {
                                                                false
                                                            }
                                                        }
                                                    }
                                                HomePageCardContent(
                                                    index = index,
                                                    item = item,
                                                    onClick = onClick,
                                                    onLongClick = onLongClick,
                                                    viewOptions = viewOptions,
                                                    modifier =
                                                        cardModifier
                                                            .onFocusChanged { onFocus(it.isFocused) }
                                                            .onKeyEvent { onKey(it) },
                                                )
                                            },
                                            showViewMore = showViewMore && row.showViewMore,
                                            viewMoreCardContent = { mod ->
                                                HomePageViewMoreCard(
                                                    isEpisode = row.items.last()?.type == BaseItemKind.EPISODE,
                                                    onClick = {
                                                        onClickViewMore.invoke(
                                                            RowColumn(
                                                                rowIndex,
                                                                r.items.size,
                                                            ),
                                                            r,
                                                        )
                                                    },
                                                    onLongClick = {},
                                                    viewOptions = viewOptions,
                                                    modifier =
                                                        mod.onFocusChanged {
                                                            if (it.isFocused) {
                                                                currentOnFocusPosition.invoke(
                                                                    RowColumn(
                                                                        rowIndex,
                                                                        r.items.size,
                                                                    ),
                                                                )
                                                            }
                                                        },
                                                )
                                            },
                                        )
                                    } else if (showEmptyRows) {
                                        FocusableItemRow(
                                            title = r.title.getString(),
                                            subtitle = stringResource(R.string.no_results),
                                            modifier = rowModifier,
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        when (loadingState) {
            LoadingState.Pending,
            LoadingState.Loading,
            -> {
                Box(
                    modifier =
                        Modifier
                            .padding(if (showClock) 40.dp else 20.dp)
                            .size(40.dp)
                            .align(Alignment.TopEnd),
                ) {
                    CircularProgress(Modifier.fillMaxSize())
                }
            }

            else -> {}
        }
    }
}

private const val HOME_ACQUIRING_ROW_KEY = "acquiring"
internal const val HOME_ACQUIRING_MORE_KEY = "acquiring:more"
private val homeRowBottomPadding = 8.dp

internal fun configuredHomeRowKey(index: Int) = "configured:$index"

internal fun MediaKey.composeSaveableKey(): String =
    when (this) {
        is MediaKey.Catalog -> {
            "acquiring:${mediaType.name}:$tmdbId"
        }

        is MediaKey.Season -> {
            val catalog = series as MediaKey.Catalog
            "acquiring:${catalog.mediaType.name}:${catalog.tmdbId}:season:$seasonNumber"
        }

        else -> {
            error("Unsupported Home acquisition key: $this")
        }
    }

private val MediaKey.homeTmdbId: Int
    get() =
        when (this) {
            is MediaKey.Catalog -> tmdbId
            is MediaKey.Season -> (series as MediaKey.Catalog).tmdbId
            else -> error("Unsupported Home acquisition key: $this")
        }

private val MediaKey.homeCatalogMediaType: CatalogMediaType
    get() =
        when (this) {
            is MediaKey.Catalog -> mediaType
            is MediaKey.Season -> (series as MediaKey.Catalog).mediaType
            else -> error("Unsupported Home acquisition key: $this")
        }

internal sealed interface AcquiringFocusResolution {
    data class Card(
        val key: MediaKey,
    ) : AcquiringFocusResolution

    data object ConfiguredFallback : AcquiringFocusResolution

    data object Unchanged : AcquiringFocusResolution
}

internal fun resolveAcquiringFocus(
    acquiringHadFocus: Boolean,
    previousKeys: List<MediaKey>,
    currentKeys: List<MediaKey>,
    focusedKey: MediaKey?,
): AcquiringFocusResolution {
    if (!acquiringHadFocus) return AcquiringFocusResolution.Unchanged
    if (focusedKey == null || focusedKey in currentKeys) return AcquiringFocusResolution.Unchanged
    if (currentKeys.isEmpty()) return AcquiringFocusResolution.ConfiguredFallback
    val previousIndex = previousKeys.indexOf(focusedKey).coerceAtLeast(0)
    return AcquiringFocusResolution.Card(currentKeys[previousIndex.coerceAtMost(currentKeys.lastIndex)])
}

@Composable
private fun HomeAcquiringRow(
    items: List<HomeAcquiringItem>,
    focusRequesters: Map<MediaKey, FocusRequester>,
    onClick: (HomeAcquiringItem) -> Unit,
    onClickMore: () -> Unit,
    onFocus: (MediaKey) -> Unit,
    modifier: Modifier = Modifier,
) {
    ItemRow(
        title = stringResource(R.string.acquiring),
        items = items,
        onClickItem = { _, acquiring -> onClick(acquiring) },
        onLongClickItem = { _, _ -> },
        itemKey = { _, acquiring -> requireNotNull(acquiring).key.composeSaveableKey() },
        horizontalPadding = 16.dp,
        showViewMore = true,
        viewMoreKey = HOME_ACQUIRING_MORE_KEY,
        modifier = modifier.fillMaxWidth().focusGroup(),
        cardContent = { _, acquiring, itemModifier, itemOnClick, _ ->
            if (acquiring != null) {
                val cardModifier =
                    itemModifier
                        .focusRequester(focusRequesters.getValue(acquiring.key))
                        .onFocusChanged {
                            if (it.isFocused) onFocus(acquiring.key)
                        }
                HomeAcquiringPosterCard(acquiring, itemOnClick, cardModifier)
            }
        },
        viewMoreCardContent = { itemModifier ->
            ViewMoreCard(
                onClick = onClickMore,
                onLongClick = {},
                showTitle = false,
                modifier = itemModifier,
            )
        },
    )
}

@Composable
private fun HomeAcquiringPosterCard(
    acquiring: HomeAcquiringItem,
    onClick: () -> Unit,
    modifier: Modifier,
) {
    val presentation = acquiring.artworkPresentation()
    Card(
        onClick = onClick,
        onLongClick = {},
        modifier = modifier.size(Cards.height2x3 * AspectRatios.TALL, Cards.height2x3),
        colors = CardDefaults.colors(),
    ) {
        Box(Modifier.fillMaxSize()) {
            ItemCardImage(
                imageUrl = acquiring.item.posterUrl,
                name = acquiring.item.title,
                showOverlay = false,
                favorite = false,
                watched = false,
                unwatchedCount = 0,
                watchedPercent = null,
                numberOfVersions = 0,
                useFallbackText = true,
                contentScale = ContentScale.FillBounds,
                mediaPresentation = presentation.mediaPresentation,
                modifier = Modifier.fillMaxSize(),
            )
            presentation.mediaPresentation.acquisitionState?.let {
                AcquisitionStateIndicator(
                    state = it,
                    modifier = Modifier.align(Alignment.TopStart),
                )
            }
            presentation.seasonBadge?.let {
                HomeAcquiringSeasonIndicator(
                    text = it,
                    modifier = Modifier.align(Alignment.TopEnd),
                )
            }
        }
    }
}

@Composable
private fun HomeAcquiringSeasonIndicator(
    text: String,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier =
            modifier
                .padding(4.dp)
                .background(AppColors.TransparentBlack50, RoundedCornerShape(25)),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.padding(4.dp),
        )
    }
}

@Composable
private fun HomeAcquiringHeader(
    item: DiscoverItem,
    showLogo: Boolean,
    modifier: Modifier = Modifier,
) {
    HomePageHeader(
        title = item.title,
        subtitle = item.subtitle ?: item.releaseDate?.year?.toString(),
        overview = item.overview,
        overviewTwoLines = false,
        quickDetails = null,
        timeRemaining = null,
        endsAt = null,
        showLogo = showLogo,
        logoImageUrl = item.logoUrl,
        modifier = modifier,
    )
}

internal fun HomeAcquiringItem.cardPresentation(): CardMediaPresentation =
    acquisitionPresentation
        ?: CardMediaPresentation(acquisitionState = CardAcquisitionState.ACQUIRING)

internal data class HomeAcquiringArtworkPresentation(
    val mediaPresentation: CardMediaPresentation,
    val seasonBadge: String?,
)

internal fun HomeAcquiringItem.artworkPresentation(): HomeAcquiringArtworkPresentation =
    HomeAcquiringArtworkPresentation(
        mediaPresentation = cardPresentation(),
        seasonBadge = seasonNumber?.let { "S$it" },
    )

internal fun HomeAcquiringItem.destination(): Destination =
    verifiedJellyfinItemId?.let { itemId ->
        if (seasonNumber != null) {
            verifiedSeriesDestination(itemId, verifiedJellyfinSeasonId, seasonNumber)
        } else {
            Destination.MediaItem(itemId = itemId, type = BaseItemKind.MOVIE)
        }
    } ?: Destination.DiscoveredItem(item)

internal fun homeAcquiringMoreDestination(): Destination = Destination.Downloads

@Composable
fun HomePageHeader(
    item: BaseItem?,
    showLogo: Boolean,
    modifier: Modifier = Modifier,
) {
    val isEpisode = item?.type == BaseItemKind.EPISODE
    val dto = item?.data
    HomePageHeader(
        title = item?.title,
        subtitle = if (isEpisode) dto?.name else null,
        overview = dto?.overview,
        overviewTwoLines = isEpisode,
        quickDetails = item?.ui?.quickDetails,
        timeRemaining = item?.timeRemainingOrRuntime,
        endsAt = item?.data?.endDate,
        showLogo = showLogo,
        logoImageUrl = rememberLogoUrl(item),
        modifier = modifier,
    )
}

@Composable
fun HomePageHeader(
    title: String?,
    subtitle: String?,
    overview: String?,
    overviewTwoLines: Boolean,
    quickDetails: QuickDetailsData?,
    timeRemaining: Duration?,
    endsAt: DateTime?,
    showLogo: Boolean,
    logoImageUrl: String?,
    modifier: Modifier = Modifier,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(4.dp),
        modifier = modifier,
    ) {
        TitleOrLogo(
            title = title,
            logoImageUrl = logoImageUrl,
            showLogo = showLogo,
            modifier = Modifier.fillMaxWidth(.75f),
        )
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier =
                Modifier
                    .fillMaxWidth(.6f),
        ) {
            if (subtitle != null) {
                EpisodeName(subtitle)
            }
            QuickDetails(quickDetails, timeRemaining, endsAt = endsAt)
            val overviewModifier =
                Modifier
                    .padding(0.dp)
                    .height(48.dp + if (!overviewTwoLines) 12.dp else 0.dp)
                    .width(400.dp)
            if (overview.isNotNullOrBlank()) {
                Text(
                    text = overview,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = if (overviewTwoLines) 2 else 3,
                    overflow = TextOverflow.Ellipsis,
                    modifier = overviewModifier,
                )
            } else {
                Spacer(overviewModifier)
            }
        }
    }
}

@Composable
fun HomePageCardContent(
    index: Int,
    item: BaseItem?,
    onClick: () -> Unit,
    onLongClick: () -> Unit,
    viewOptions: HomeRowViewOptions,
    modifier: Modifier,
) {
    when (item?.type) {
        BaseItemKind.GENRE -> {
            GenreCard(
                genreId = item.id,
                name = item.name,
                imageUrl = item.imageUrlOverride,
                onClick = onClick,
                onLongClick = onLongClick,
                modifier = modifier.height(viewOptions.heightDp.dp),
            )
        }

        BaseItemKind.STUDIO -> {
            StudioCard(
                studioId = item.id,
                name = item.name,
                imageUrl = item.imageUrlOverride,
                onClick = onClick,
                onLongClick = onLongClick,
                modifier = modifier.height(viewOptions.heightDp.dp),
            )
        }

        else -> {
            val imageType =
                remember(item, viewOptions) {
                    if (item?.type == BaseItemKind.EPISODE) {
                        viewOptions.episodeImageType.imageType
                    } else {
                        viewOptions.imageType.imageType
                    }
                }
            val ratio =
                remember(item, viewOptions) {
                    if (item?.type == BaseItemKind.EPISODE) {
                        viewOptions.episodeAspectRatio.ratio
                    } else {
                        viewOptions.aspectRatio.ratio
                    }
                }
            val scale =
                remember(item, viewOptions) {
                    if (item?.type == BaseItemKind.EPISODE) {
                        viewOptions.episodeContentScale.scale
                    } else {
                        viewOptions.contentScale.scale
                    }
                }
            if (viewOptions.showTitles) {
                BannerCardWithTitle(
                    title = item?.title,
                    subtitle = item?.subtitle,
                    item = item,
                    aspectRatio = ratio,
                    imageType = imageType,
                    imageContentScale = scale,
                    cornerText = item?.ui?.episodeUnplayedCornerText,
                    played = item?.data?.userData?.played ?: false,
                    favorite = item?.favorite ?: false,
                    playPercent =
                        item?.data?.userData?.playedPercentage
                            ?: 0.0,
                    onClick = onClick,
                    onLongClick = onLongClick,
                    modifier = modifier,
                    cardHeight = viewOptions.heightDp.dp,
                    useSeriesForPrimary = viewOptions.useSeries,
                )
            } else {
                BannerCard(
                    name = item?.data?.seriesName ?: item?.name,
                    item = item,
                    aspectRatio = ratio,
                    imageType = imageType,
                    imageContentScale = scale,
                    cornerText = item?.ui?.episodeUnplayedCornerText,
                    played = item?.data?.userData?.played ?: false,
                    favorite = item?.favorite ?: false,
                    playPercent =
                        item?.data?.userData?.playedPercentage
                            ?: 0.0,
                    onClick = onClick,
                    onLongClick = onLongClick,
                    modifier = modifier,
                    interactionSource = null,
                    cardHeight = viewOptions.heightDp.dp,
                    useSeriesForPrimary = viewOptions.useSeries,
                )
            }
        }
    }
}

@Composable
fun HomePageViewMoreCard(
    isEpisode: Boolean,
    onClick: () -> Unit,
    onLongClick: () -> Unit,
    viewOptions: HomeRowViewOptions,
    modifier: Modifier,
) {
    val aspectRatio =
        remember(isEpisode, viewOptions) {
            if (isEpisode) {
                viewOptions.episodeAspectRatio
            } else {
                viewOptions.aspectRatio
            }
        }
    ViewMoreCard(
        onClick = onClick,
        onLongClick = onLongClick,
        modifier = modifier,
        aspectRatio = aspectRatio,
        size = DpSize(height = viewOptions.heightDp.dp, width = Dp.Unspecified),
        showTitle = viewOptions.showTitles,
    )
}
