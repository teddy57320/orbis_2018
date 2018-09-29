import com.orbischallenge.snake.client.objects.models.EnemyUnit;
import com.orbischallenge.snake.client.objects.models.FriendlyUnit;
import com.orbischallenge.snake.client.objects.models.World;
import com.orbischallenge.snake.client.objects.models.Tile;
import com.orbischallenge.game.engine.Point;
import java.util.*;

public class PlayerAI {
    private Tile target;
    private int turnCount;
    private boolean outbound;

    public PlayerAI() {
        turnCount = 0;
        target = null;
        outbound = true;
    }

    /**
     * This method is called every turn by the game engine.
     * Make sure you call friendlyUnit.move(Point target) somewhere here!
     *
     * Below, you'll find a very rudimentary strategy to get you started.
     * Feel free to use, or delete any part of the provided code - Good luck!
     *
     * @param world world object (more information on the documentation)
     *       - world: contains information about the game map.
     *       - world.path: contains various pathfinding helper methods.
     *       - world.util: contains various tile-finding helper methods.
     *       - world.fill: contains various flood-filling helper methods.
     *
     * @param friendlyUnit FriendlyUnit object
     * @param enemyUnits list of EnemyUnit objects
     */
    public void doMove(World world, FriendlyUnit friendlyUnit, EnemyUnit[] enemyUnits) {
        // increment turn count
        turnCount ++;

        // if unit is dead, stop making moves.
        // note that the unit's status is null on turn 0.
        if (friendlyUnit.getStatus() != null && friendlyUnit.getStatus().equals("DISABLED")) {
            target = null;
            outbound = true;
            System.out.println(String.format("Turn %s: Disabled - skipping move.", String.valueOf(turnCount)));
            return;
        }

        // if unit reaches the target point, reverse outbound boolean and set target back to null
        if (target != null && friendlyUnit.getPosition().equals(target.getPosition())) {
            outbound = !outbound;
            target = null;
        }

        // if outbound and no target set, set target as the closest capturable tile at least 1 tile from your territory's edge.
        if (outbound && target == null) {
            Set<Tile> edges = world.util.getFriendlyTerritoryEdges();
            List<Point> avoid = new ArrayList<>();
            for (Tile edge : edges) {
                avoid.addAll(world.getNeighbours(edge.getPosition()).values());
            }
            target = world.util.getClosestCapturableTerritoryFrom(friendlyUnit.getPosition(), avoid);
        }

        // else if inbound and no target set, set target as the closest friendly tile.
        else if (!outbound && target == null) {
            target = world.util.getClosestFriendlyTerritoryFrom(friendlyUnit.getPosition(), null);
        }

        // set next move as the next point in path to target
        Point nextMove = world.path.getShortestPath(friendlyUnit.getPosition(), target.getPosition(), friendlyUnit.getSnake()).get(0);

        // move!
        friendlyUnit.move(nextMove);
        System.out.println(String.format(
            "Turn %s: currently at %s, making %s move to %s",
            String.valueOf(turnCount),
            friendlyUnit.getPosition().toString(),
            outbound ? "outbound" : "inbound",
            target.getPosition().toString()
        ));
    }
}
