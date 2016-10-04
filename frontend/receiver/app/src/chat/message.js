import { cheerColor, cheerEmote } from './cheers.js'

const defaultColors = [
  '#FF0000', '#0000FF', '#00FF00', '#B22222', '#FF7F50',
  '#9ACD32', '#FF4500', '#2E8B57', '#DAA520', '#D2691E',
  '#5F9EA0', '#1E90FF', '#FF69B4', '#8A2BE2', '#00FF7F'
]

const badgeTypes = [
  'global_mod', 'admin', 'broadcaster',
  'mod', 'staff', 'turbo', 'subscriber'
]

const cheerPattern = /^cheer(\d+)$/

// https://discuss.dev.twitch.tv/t/default-user-color-in-chat/385
function defaultColor(name) {
  let n = name.charCodeAt(0) + name.charCodeAt(name.length - 1)

  return defaultColors[n % defaultColors.length]
}

function getBadges(message) {
  let mTags = (message.tags || {})
  let badgeMap = {}
  let badges = []

  if (mTags.badges)
    mTags.badges.split(',').forEach(badge => {
      let splitted = badge.split('/')
      badgeMap[splitted[0]] = splitted[1]
    })

  badgeTypes.forEach(type => {
    if (badgeMap[type] == '1')
      badges.push(type)
  })

  if (badgeMap.moderator) // I noticed this inconsistency...
    badges.push('mod')
  if (badgeMap.bits)
    badges.push('bits' + badgeMap.bits)

  return badges
}

function buildChatLine(message, store) {
  let li = $('<li>')
    .addClass('chat-line')

  let badges = getBadges(message)

  if (badges.length) {
    let badgeSpan = $('<span>')
      .addClass('badge-wrapper')

    let div = $('<div>')
      .addClass('badge-container')

    badges.forEach(badge => {
      let img = $('<img>')
        .attr('src', store.badges.get(badge))
        .addClass('badge')

      div.append(img)
    })

    badgeSpan.append(div)
    li.append(badgeSpan)
  }

  let mTags = (message.tags || {})
  let color = (mTags.color || defaultColor(message.sender))

  let nameSpan = $('<span>')
    .addClass('chat-line-sender')
    .text(mTags['display-name'] || message.sender)
    .css('color', color)

  let htmlParts = message.content.split(' ').map(function(word) {
    if (store.emotes.has(word))
      return `<img src="${store.emotes.get(word)}">`

    if (mTags.bits) {
      let match = word.match(cheerPattern)
      if (match)
        return `<img src="${cheerEmote(match[1])}">` +
               `<span style="color: ${cheerColor(match[1])};">${match[1]}</span>`
    }

    return word
  })

  let contentSpan = $('<span>').html(`: ${htmlParts.join(' ')}`)

  li.append(nameSpan)
  li.append(contentSpan)

  return li
}

module.exports = {
  buildChatLine: buildChatLine
}