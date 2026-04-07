import { loadConfig } from './core/config.js';
import { TrelloService } from './services/trello.js';

async function main() {
  const config = loadConfig();
  const trello = new TrelloService(config.trello);

  const command = process.argv[2];

  switch (command) {
    case 'board': {
      const result = await trello.getBoard();
      if (!result.success) {
        console.error('Error:', result.error);
        process.exit(1);
      }
      console.log(`Board: ${result.data!.name}`);
      console.log(`URL: ${result.data!.url}`);
      if (result.data!.desc) console.log(`Description: ${result.data!.desc}`);
      break;
    }

    case 'lists': {
      const result = await trello.getLists();
      if (!result.success) {
        console.error('Error:', result.error);
        process.exit(1);
      }
      console.log('Lists:');
      for (const list of result.data!) {
        console.log(`  - ${list.name} (${list.id})`);
      }
      break;
    }

    case 'cards': {
      const listId = process.argv[3];
      const listsResult = await trello.getLists();
      const cardsResult = await trello.getCards(listId);
      if (!cardsResult.success) {
        console.error('Error:', cardsResult.error);
        process.exit(1);
      }
      const listMap = new Map(
        (listsResult.data ?? []).map((l) => [l.id, l.name]),
      );

      if (cardsResult.data!.length === 0) {
        console.log('No cards found.');
        break;
      }

      let currentList = '';
      const sorted = [...cardsResult.data!].sort((a, b) => a.idList.localeCompare(b.idList));
      for (const card of sorted) {
        const listName = listMap.get(card.idList) ?? card.idList;
        if (listName !== currentList) {
          currentList = listName;
          console.log(`\n[${currentList}]`);
        }
        const labels = card.labels.length > 0
          ? ` [${card.labels.map((l) => l.name || l.color).join(', ')}]`
          : '';
        const due = card.due ? ` (due: ${new Date(card.due).toLocaleDateString()})` : '';
        console.log(`  - ${card.name}${labels}${due}`);
      }
      console.log();
      break;
    }

    case 'add': {
      const listId = process.argv[3];
      const name = process.argv[4];
      if (!listId || !name) {
        console.error('Usage: add <list-id> <card-name> [description]');
        process.exit(1);
      }
      const desc = process.argv[5] ?? '';
      const result = await trello.createCard(listId, name, desc);
      if (!result.success) {
        console.error('Error:', result.error);
        process.exit(1);
      }
      console.log(`Created card: ${result.data!.name}`);
      console.log(`URL: ${result.data!.url}`);
      break;
    }

    case 'move': {
      const cardId = process.argv[3];
      const targetListId = process.argv[4];
      if (!cardId || !targetListId) {
        console.error('Usage: move <card-id> <target-list-id>');
        process.exit(1);
      }
      const result = await trello.moveCard(cardId, targetListId);
      if (!result.success) {
        console.error('Error:', result.error);
        process.exit(1);
      }
      console.log(`Moved card: ${result.data!.name}`);
      break;
    }

    default:
      console.log('Oleg-helper Trello Integration\n');
      console.log('Commands:');
      console.log('  board           Show board info');
      console.log('  lists           Show all lists');
      console.log('  cards [listId]  Show cards (optionally filtered by list)');
      console.log('  add <listId> <name> [desc]  Create a new card');
      console.log('  move <cardId> <listId>      Move a card to another list');
      break;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
